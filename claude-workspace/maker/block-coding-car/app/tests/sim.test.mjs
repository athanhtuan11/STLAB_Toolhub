// Gate: mo phong app (src/sim.js) = ban tham chieu protocol/golden.json (cung bo ca voi firmware).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { expand, simulate } from '../src/sim.js';

const golden = JSON.parse(readFileSync(new URL('../../protocol/golden.json', import.meta.url), 'utf8'));

for (const c of golden.cases) {
  test(`golden ${c.name}`, () => {
    const r = expand(c.doc);
    if (c.ok) {
      assert.deepEqual(r, { ok: true, steps: c.steps });
      const s = simulate(r.steps, golden.start, golden.size);
      assert.deepEqual(s, c.sim);
    } else {
      assert.deepEqual(r, { ok: false, code: c.code });
    }
  });
}

test('expand khong sua doc dau vao', () => {
  const doc = { v: 1, prog: [{ id: 0, op: 'repeat', n: 2, body: [{ id: 1, op: 'fwd' }] }] };
  const before = JSON.stringify(doc);
  expand(doc);
  assert.equal(JSON.stringify(doc), before);
});

test('simulate mac dinh xuat phat 0,5,N luoi 6', () => {
  assert.deepEqual(simulate([[0, 'fwd', 1]]), { trace: [[0, 4, 'N']], final: [0, 4, 'N'], edge: null });
});

test('expand nhan doc khong phai object', () => {
  assert.deepEqual(expand(null), { ok: false, code: 'bad_json' });
  assert.deepEqual(expand([1]), { ok: false, code: 'bad_json' });
});
