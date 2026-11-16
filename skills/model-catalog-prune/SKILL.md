---
name: "model-catalog-prune"
description: "Prune unusable models from the OpenClaw catalog: probe providers, classify failures, rewrite models.providers, verify with a real agent turn."
---

# Model Catalog Prune

Goal: leave only models that actually answer a completion request, and prove each one still answers.

`openclaw models list` shows `available: true` for every catalog row, including dead providers. Catalog
presence is not usability. Only a live completion request proves a model works.

## Step 1: Inventory the catalog and the config

```bash
openclaw models list --json          # every key, input modality, context window
openclaw models status                # default, fallbacks, auth sources per provider
```

Read the active config to see which providers are explicitly configured versus inherited from the
built-in catalog:

```bash
python3 -c "
import json; d=json.load(open('$HOME/.openclaw/openclaw.json'))
print(list(d.get('models',{}).get('providers',{}).keys()))
print(d.get('models',{}).get('mode'))
"
```

Note the default and fallback models. Both must survive the prune, and the fallback must be one you
verified.

## Step 2: Get the API key OpenClaw actually uses

Environment variables for a provider can be stale while a saved auth profile works. Probe with the key
OpenClaw resolves, not with the shell variable. `openclaw models status` prints the source per
provider; if the profile key differs from the env key, take the profile key.

External `sqlite3` cannot open the live OpenClaw state directory. Copy the database out first, then
extract the key from the copy:

```bash
cp ~/.openclaw/state/openclaw.sqlite /tmp/oc_state_copy.sqlite
python3 - <<'EOF'
import sqlite3, re
c = sqlite3.connect('/tmp/oc_state_copy.sqlite')
for (v,) in c.execute("select value_json from config_machine_state"):
    if isinstance(v, str) and 'sk-cp-' in v:
        m = re.findall(r'"(sk-cp-[^"\\]{10,200})"', v)
        if m:
            open('/tmp/provider_key.txt', 'w').write(m[0]); break
EOF
```

Keep the key in a file and reference it in curl. Never print it to the chat transcript and never
inline it into a config file — configs take `${ENV_VAR}` references.

## Step 3: Probe every candidate model

One minimal completion per model, generous timeout, capture the HTTP status and body:

```bash
KEY=$(cat /tmp/provider_key.txt)
for m in MiniMax-M3 MiniMax-M2.7; do
  code=$(curl -s -o /tmp/probe.json -w '%{http_code}' -m 30 \
    https://api.example.com/v1/chat/completions \
    -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
    -d "{\"model\":\"$m\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":8}")
  echo "[$code] $m"
done
```

Classify each status:

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | usable | keep |
| 401 | key invalid for this endpoint | provider unusable unless another key works |
| 403 | quota exhausted | provider unusable until topped up |
| 404 | model not on this endpoint | drop the model |
| 410 | model EOL at the provider | drop the model |
| 000 | timeout | unverified: re-probe once with a longer timeout before deciding |

A 000 on a large model is often cold start, not breakage. Re-probe with 90s. Two consecutive timeouts
means unverified, and unverified models stay out of the catalog.

Also probe the host itself when a local or LAN provider fails, to separate "model broken" from
"service down":

```bash
curl -s -m 8 http://192.168.0.140:11434/v1/models
timeout 3 bash -c "</dev/tcp/192.168.0.140/8080" && echo open || echo closed
```

## Step 4: Rewrite the catalog

`models.mode` controls the catalog root:

- `merge` (default) keeps built-in provider rows, so broken models cannot be removed.
- `replace` uses only the providers you define in `models.providers`.

Set `mode: "replace"` and define each surviving provider explicitly with its verified models only.
Delete providers whose every model failed by setting the provider to `null` in the patch.

Build the patch as a file and validate before writing:

```bash
openclaw config patch --file /tmp/models.patch.json --dry-run
openclaw config patch --file /tmp/models.patch.json
```

Two schema details that make the dry run fail:

- `models.providers.<id>.models[].input` is an array: `["text","image"]`, never the string `"text+image"`.
- `contextWindow` and `maxTokens` are required per model; copy them from `openclaw models list --json`.

`models` is a hot-reload path — no gateway restart is needed.

Keep the provider `apiKey` as a `${ENV_VAR}` reference. If the env variable is the broken one, point
it at a valid one or note the stale variable for the user; do not paste a literal key into config.

## Step 5: Verify end to end

The list is not proof. Run a real agent turn on the default model, the fallback, and one model from
each newly added provider:

```bash
openclaw agent --model provider/model-id --session-id prunetest-1 -m "Reply with exactly: OK"
```

A provider can appear in the list and still fail on the OpenClaw auth path, so this turn is the only
real check. Also confirm the fallback chain still resolves:

```bash
openclaw models status | head -8
```

## Step 6: Report

Give Pigo a table of what stayed, what was dropped, and the reason for each drop family (401 key,
403 quota, 404 missing, 410 EOL, timeout, host down), plus a count before and after. Call out
separately that a provider was dropped for a fixable reason (out of credit, service down, stale env
key) so it can be restored later without redoing the probe.

## Pitfalls

- Do not trust `available: true` from `openclaw models list`; it means the row exists, not that it works.
- Do not trust a provider's shell env key; a saved auth profile may hold the working one.
- Do not print keys into the transcript; write them to a file and reference the file.
- Do not delete a provider that is merely out of credit without saying so; it is one config line to restore.
- Do not drop the current default or fallback without replacing it with a verified model.
