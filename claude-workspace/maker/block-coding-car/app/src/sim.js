// sim.js - interpreter + grid simulation, mirror of protocol/PROTOCOL.md sections 1-3.
// The Python reference (protocol/make_golden.py) is the source of truth for every rule here.

const OPS = {
  fwd: [1, 4, 1],
  back: [1, 4, 1],
  left: null,
  right: null,
  sound: [0, 2, 0],
  eye: [0, 5, 0],
  repeat: [2, 4, 2]
};

const MAX_BLOCKS = 12;
const MAX_BODY = 6;

function isInt(v) {
  return typeof v === 'number' && Number.isInteger(v);
}

export function expand(doc) {
  if (!doc || typeof doc !== 'object' || Array.isArray(doc) || !('prog' in doc)) {
    return { ok: false, code: 'bad_json' };
  }
  if (doc.v !== 1) {
    return { ok: false, code: 'bad_version' };
  }
  const prog = doc.prog;
  if (!Array.isArray(prog)) {
    return { ok: false, code: 'bad_json' };
  }
  if (prog.length === 0) {
    return { ok: false, code: 'empty' };
  }

  const ids = new Set();
  let count = 0;
  let err = null;

  function check(blk, inside) {
    if (!blk || typeof blk !== 'object' || Array.isArray(blk)) {
      err = 'bad_json';
      return null;
    }
    const op = blk.op;
    if (!Object.prototype.hasOwnProperty.call(OPS, op)) {
      err = 'bad_op';
      return null;
    }
    const bid = blk.id;
    if (!isInt(bid) || bid < 0 || bid > 999) {
      err = 'bad_arg';
      return null;
    }
    if (ids.has(bid)) {
      err = 'dup_id';
      return null;
    }
    ids.add(bid);
    count += 1;

    const rng = OPS[op];
    let arg = 0;
    if (rng) {
      const lo = rng[0];
      const hi = rng[1];
      const dflt = rng[2];
      const n = 'n' in blk ? blk.n : dflt;
      if (!isInt(n) || n < lo || n > hi) {
        err = 'bad_arg';
        return null;
      }
      arg = n;
    }

    if (op === 'repeat') {
      if (inside) {
        err = 'nested_repeat';
        return null;
      }
      const body = blk.body;
      if (!Array.isArray(body) || body.length === 0) {
        err = 'empty_repeat';
        return null;
      }
      if (body.length > MAX_BODY) {
        err = 'too_many_blocks';
        return null;
      }
      let bodySteps = [];
      for (const b of body) {
        const part = check(b, true);
        if (err) {
          return null;
        }
        bodySteps = bodySteps.concat(part);
      }
      const out = [];
      for (let k = 0; k < arg; k += 1) {
        out.push.apply(out, bodySteps);
      }
      return out;
    }

    return [[bid, op, arg]];
  }

  let steps = [];
  for (const b of prog) {
    const part = check(b, false);
    if (err) {
      return { ok: false, code: err };
    }
    steps = steps.concat(part);
  }
  if (count > MAX_BLOCKS) {
    return { ok: false, code: 'too_many_blocks' };
  }
  return { ok: true, steps: steps };
}

const DIRS = ['N', 'E', 'S', 'W'];
const DXY = { N: [0, -1], E: [1, 0], S: [0, 1], W: [-1, 0] };

export function simulate(steps, start, size) {
  const st = start || [0, 5, 'N'];
  const lim = size || 6;
  let x = st[0];
  let y = st[1];
  let h = st[2];
  const trace = [];
  let edge = null;

  for (const step of steps) {
    const bid = step[0];
    const op = step[1];
    const arg = step[2];
    if (op === 'fwd' || op === 'back') {
      let dx = DXY[h][0];
      let dy = DXY[h][1];
      if (op === 'back') {
        dx = -dx;
        dy = -dy;
      }
      for (let k = 0; k < arg; k += 1) {
        const nx = x + dx;
        const ny = y + dy;
        if (!(nx >= 0 && nx < lim && ny >= 0 && ny < lim)) {
          edge = bid;
          break;
        }
        x = nx;
        y = ny;
      }
    } else if (op === 'left') {
      h = DIRS[(DIRS.indexOf(h) + 3) % 4];
    } else if (op === 'right') {
      h = DIRS[(DIRS.indexOf(h) + 1) % 4];
    }
    trace.push([x, y, h]);
    if (edge !== null) {
      break;
    }
  }

  return { trace: trace, final: [x, y, h], edge: edge };
}
