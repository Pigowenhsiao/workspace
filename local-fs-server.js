// local-fs-server.js
const fs = require('fs');
const path = require('path');
const ROOT_DIR = '/home/pigo/workspace'; // 請改成你要暴露的根目錄
const IMPLICIT_ROOT = path.resolve(ROOT_DIR);

function safeJoin(userPath) {
  const p = path.resolve(IMPLICIT_ROOT, userPath);
  if (!p.startsWith(IMPLICIT_ROOT)) {
    throw new Error('Access outside allowed root');
  }
  return p;
}

function readFile(p) {
  const abs = safeJoin(p);
  return fs.promises.readFile(abs, 'utf8')
    .then(content => ({ ok: true, content }))
    .catch(err => ({ ok: false, error: err.message }));
}

function writeFile(p, content) {
  const abs = safeJoin(p);
  return fs.promises.writeFile(abs, content, 'utf8')
    .then(() => ({ ok: true }))
    .catch(err => ({ ok: false, error: err.message }));
}

function listDir(p) {
  const abs = safeJoin(p);
  return fs.promises.readdir(abs, { withFileTypes: true })
    .then(entries => {
      const items = entries.map(e => ({
        name: e.name,
        type: e.isDirectory() ? 'dir' : 'file'
      }));
      return { ok: true, items };
    })
    .catch(err => ({ ok: false, error: err.message }));
}

// 逐行從 stdin 接收 JSON 指令
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: false });

rl.on('line', async (line) => {
  line = line.trim();
  if (!line) return;
  let req;
  try {
    req = JSON.parse(line);
  } catch (e) {
    process.stdout.write(JSON.stringify({ ok: false, error: 'invalid json' }) + '\n');
    return;
  }

  const action = req.action;
  try {
    let res;
    if (action === 'readFile') {
      res = await readFile(req.path || '');
    } else if (action === 'writeFile') {
      res = await writeFile(req.path || '', req.content || '');
    } else if (action === 'listDir') {
      res = await listDir(req.path || '');
    } else {
      res = { ok: false, error: 'unknown action' };
    }
    process.stdout.write(JSON.stringify(res) + '\n');
  } catch (err) {
    process.stdout.write(JSON.stringify({ ok: false, error: err.message }) + '\n');
  }
});

// 安全退出
process.on('SIGINT', () => process.exit(0));
