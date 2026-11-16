// Gate: dung chuong trinh tu dai lenh (src/program.js) + trang thai ket noi xe (src/carlink.js).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { LEVELS, buildDoc, countBlocks, canAdd } from '../src/program.js';
import { initialState, reduce, msgRun, msgStop, msgHello } from '../src/carlink.js';
import { expand } from '../src/sim.js';

test('LEVELS dung bo khoi rut gon da chot', () => {
  assert.deepEqual([...LEVELS[1].ops].sort(), ['back', 'fwd', 'left', 'right']);
  assert.deepEqual([...LEVELS[2].ops].sort(), ['back', 'eye', 'fwd', 'left', 'repeat', 'right', 'sound']);
  assert.deepEqual([...LEVELS[3].ops].sort(), [...LEVELS[2].ops].sort());
  assert.equal(LEVELS[1].maxBlocks, 8);
  assert.equal(LEVELS[2].maxBlocks, 8);
  assert.equal(LEVELS[3].maxBlocks, 12);
  assert.equal(LEVELS[1].counts, false);
  assert.equal(LEVELS[3].counts, true);
});

test('buildDoc danh id 0.. theo thu tu duyet truoc, hop le voi expand', () => {
  const strip = [
    { op: 'fwd', n: 2 },
    { op: 'repeat', n: 3, body: [{ op: 'left' }, { op: 'sound', n: 1 }] },
    { op: 'eye', n: 4 },
  ];
  const doc = buildDoc(strip);
  assert.deepEqual(doc, {
    v: 1,
    prog: [
      { id: 0, op: 'fwd', n: 2 },
      { id: 1, op: 'repeat', n: 3, body: [{ id: 2, op: 'left' }, { id: 3, op: 'sound', n: 1 }] },
      { id: 4, op: 'eye', n: 4 },
    ],
  });
  assert.equal(expand(doc).ok, true);
});

test('buildDoc khong gui n cho left/right', () => {
  const doc = buildDoc([{ op: 'left', n: 3 }, { op: 'right' }]);
  assert.deepEqual(doc.prog, [{ id: 0, op: 'left' }, { id: 1, op: 'right' }]);
});

test('countBlocks dem ca repeat va body', () => {
  assert.equal(countBlocks([{ op: 'fwd' }, { op: 'repeat', n: 2, body: [{ op: 'left' }, { op: 'fwd' }] }]), 4);
  assert.equal(countBlocks([]), 0);
});

test('canAdd theo cap + gioi han', () => {
  const eight = Array.from({ length: 8 }, () => ({ op: 'fwd' }));
  assert.equal(canAdd([], 'fwd', 1), true);
  assert.equal(canAdd([], 'repeat', 1), false, 'cap 1 khong co repeat');
  assert.equal(canAdd([], 'sound', 1), false);
  assert.equal(canAdd(eight, 'fwd', 1), false, 'cap 1 toi da 8');
  assert.equal(canAdd(eight, 'fwd', 3), true, 'cap 3 toi da 12');
  const rep = [{ op: 'repeat', n: 2, body: [{ op: 'fwd' }] }];
  assert.equal(canAdd(rep, 'repeat', 2, true), false, 'khong long repeat');
  assert.equal(canAdd(rep, 'left', 2, true), true);
  const full = [{ op: 'repeat', n: 2, body: Array.from({ length: 6 }, () => ({ op: 'fwd' })) }];
  assert.equal(canAdd(full, 'left', 2, true), false, 'body toi da 6');
});

test('carlink reduce: hello/started/step/done/stopped/err/batt', () => {
  let s = initialState();
  assert.equal(s.connected, false);
  assert.equal(s.activeId, null);
  s = reduce(s, { t: 'hello', name: 'robot-do', color: '#E0453A', fw: '0.1.0', batt_mv: 5100, busy: false, steps_cell: 4054, steps_90: 1698 });
  assert.equal(s.connected, true);
  assert.equal(s.name, 'robot-do');
  assert.equal(s.color, '#E0453A');
  assert.equal(s.battMv, 5100);
  s = reduce(s, { t: 'started', n: 3 });
  assert.equal(s.running, true);
  s = reduce(s, { t: 'step', i: 1, id: 7 });
  assert.equal(s.activeId, 7);
  assert.equal(s.stepIndex, 1);
  s = reduce(s, { t: 'done' });
  assert.equal(s.running, false);
  assert.equal(s.activeId, null);
  s = reduce(s, { t: 'started', n: 1 });
  s = reduce(s, { t: 'stopped', why: 'button' });
  assert.equal(s.running, false);
  assert.equal(s.stopWhy, 'button');
  s = reduce(s, { t: 'err', code: 'batt_low', msg: 'Pin yếu' });
  assert.equal(s.lastError, 'batt_low');
  s = reduce(s, { t: 'batt', mv: 4300 });
  assert.equal(s.battMv, 4300);
  const before = JSON.stringify(s);
  reduce(s, { t: 'step', i: 0, id: 1 });
  assert.equal(JSON.stringify(s), before, 'reduce khong sua state cu');
  assert.deepEqual(reduce(s, { t: 'la-hoac' }), s);
});

test('carlink thong diep gui xe', () => {
  const doc = buildDoc([{ op: 'fwd' }]);
  assert.deepEqual(JSON.parse(msgRun(doc)), { t: 'run', prog: doc.prog });
  assert.deepEqual(JSON.parse(msgStop()), { t: 'stop' });
  assert.deepEqual(JSON.parse(msgHello()), { t: 'hello' });
});
