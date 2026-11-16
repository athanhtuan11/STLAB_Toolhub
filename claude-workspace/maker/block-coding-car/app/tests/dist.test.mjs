// Gate: build.py gop src/ thanh 1 file index.html.gz nhung vao flash xe (chay offline, khong CDN).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const appDir = fileURLToPath(new URL('..', import.meta.url));
const dir = mkdtempSync(join(tmpdir(), 'bcc-'));
const out = join(dir, 'index.html.gz');
execFileSync('python', [join(appDir, 'build.py'), '--out', out], { cwd: appDir, stdio: 'pipe' });
const gz = statSync(out).size;
const html = gunzipSync(readFileSync(out)).toString('utf8');

test('kich thuoc gzip < 150 KB', () => {
  assert.ok(gz < 150 * 1024, `gz = ${gz} B`);
  assert.ok(html.length > 5000, 'html qua ngan - nghi ma gia');
});

test('1 file, khong tai tai nguyen ngoai', () => {
  assert.match(html, /<html lang="vi">/);
  assert.match(html, /<meta charset="utf-8">/i);
  assert.doesNotMatch(html, /\b(src|href)\s*=\s*["']https?:/i);
  assert.doesNotMatch(html, /@import|url\(\s*["']?https?:/i);
  assert.doesNotMatch(html, /<script[^>]+src=/i);
  assert.doesNotMatch(html, /<link[^>]+stylesheet/i);
  assert.doesNotMatch(html, /^\s*(import|export)\s/m, 'con import/export trong ban gop');
});

test('co du thanh phan U1', () => {
  for (const id of ['btn-stop', 'btn-try', 'btn-real', 'strip', 'palette', 'grid', 'conn', 'level-1', 'level-2', 'level-3', 'btn-clear']) {
    assert.match(html, new RegExp(`id="${id}"`), `thieu #${id}`);
  }
  assert.match(html, /DỪNG/);
  for (const fn of ['expand', 'simulate', 'buildDoc', 'canAdd', 'reduce', 'msgRun']) {
    assert.match(html, new RegExp(`function\\s+${fn}\\b`), `thieu ham ${fn}`);
  }
  assert.match(html, /new WebSocket\(/);
  assert.match(html, /speechSynthesis/);
  assert.match(html, /localStorage/);
});

test('script gop cu phap dung (node --check)', () => {
  const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map((m) => m[1]).join('\n;\n');
  assert.ok(scripts.length > 3000, 'script qua ngan');
  const f = join(dir, 'all.js');
  writeFileSync(f, scripts);
  execFileSync(process.execPath, ['--check', f], { stdio: 'pipe' });
});
