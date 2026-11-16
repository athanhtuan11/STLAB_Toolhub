// program.js - level rules + build the wire program document from the command strip.
// Limits come from PROTOCOL.md section 1 and the approved brief (8/8/12 blocks).

export const LEVELS = {
  1: { ops: ['fwd', 'back', 'left', 'right'], maxBlocks: 8, counts: false },
  2: { ops: ['fwd', 'back', 'left', 'right', 'repeat', 'sound', 'eye'], maxBlocks: 8, counts: false },
  3: { ops: ['fwd', 'back', 'left', 'right', 'repeat', 'sound', 'eye'], maxBlocks: 12, counts: true }
};

const RANGE_OPS = ['fwd', 'back', 'sound', 'eye', 'repeat'];
const MAX_REPEAT_BODY = 6;

function cloneBlock(blk, nextId) {
  const out = { id: nextId.value, op: blk.op };
  nextId.value += 1;
  if (RANGE_OPS.indexOf(blk.op) !== -1 && blk.n !== undefined) {
    out.n = blk.n;
  }
  if (blk.op === 'repeat') {
    if (Array.isArray(blk.body)) {
      out.body = blk.body.map(function (b) {
        return cloneBlock(b, nextId);
      });
    } else {
      out.body = [];
    }
  }
  return out;
}

export function buildDoc(strip) {
  const nextId = { value: 0 };
  const prog = (strip || []).map(function (blk) {
    return cloneBlock(blk, nextId);
  });
  return { v: 1, prog: prog };
}

export function countBlocks(strip) {
  let n = 0;
  for (const blk of strip || []) {
    n += 1;
    if (blk.op === 'repeat' && Array.isArray(blk.body)) {
      n += blk.body.length;
    }
  }
  return n;
}

export function canAdd(strip, op, level, intoRepeat) {
  const cfg = LEVELS[level];
  if (!cfg) {
    return false;
  }
  if (cfg.ops.indexOf(op) === -1) {
    return false;
  }
  if (intoRepeat && op === 'repeat') {
    return false;
  }
  if (countBlocks(strip) + 1 > cfg.maxBlocks) {
    return false;
  }
  if (intoRepeat) {
    let target = null;
    for (const blk of strip || []) {
      if (blk.op === 'repeat') {
        target = blk;
      }
    }
    if (!target) {
      return false;
    }
    const body = Array.isArray(target.body) ? target.body : [];
    if (body.length + 1 > MAX_REPEAT_BODY) {
      return false;
    }
  }
  return true;
}
