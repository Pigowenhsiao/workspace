// OpenClaw Codex CLI Plugin
// Installs OpenAI Codex CLI as a model backend for OpenClaw
//
// Usage: After installing, reference as `codex-cli/codex` in model config

import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

export default definePluginEntry({
  id: "codex-cli",
  name: "OpenAI Codex CLI",
  description: "Integrates OpenAI Codex CLI as a CLI backend for OpenClaw text inference",

  configSchema: {
    type: "object",
    properties: {
      command: {
        type: "string",
        default: "codex",
        description: "CLI command name (codex, opencode, etc.)"
      },
      model: {
        type: "string",
        default: "gpt-4o",
        description: "Default model to use with Codex CLI"
      },
      temperature: {
        type: "number",
        default: 0.7,
        description: "Temperature for generation"
      },
      args: {
        type: "string",
        default: "",
        description: "Additional CLI arguments"
      }
    },
    additionalProperties: false,
  },

  register(api) {
    api.registerCliBackend({
      id: "codex-cli",
      name: "OpenAI Codex CLI",
      description: "OpenAI Codex CLI text inference backend",
      model: "gpt-4o",
      args: [],
      env: {},

      submit(session) {
        const config = api.getConfig?.() ?? {};
        const cmd = config.command ?? "codex";
        const model = config.model ?? "gpt-4o";
        const extraArgs = config.args ?? "";

        return {
          async *run(prompt, context) {
            const { spawn } = await import("node:child_process");
            const child = spawn(
              cmd,
              ["--model", model, "--no-color", extraArgs],
              { stdio: ["pipe", "pipe", "pipe"] }
            );

            child.stdin.write(prompt);
            child.stdin.end();

            const decoder = new TextDecoder();
            for await (const chunk of child.stdout) {
              yield { content: decoder.decode(chunk) };
            }
          },

          async close() {
            // Cleanup if needed
          }
        };
      }
    });
  },
});