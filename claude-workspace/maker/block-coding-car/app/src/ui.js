// ui.js - DOM layer for the block-coding-car app (U1 layout).
import { expand, simulate } from './sim.js';
import { LEVELS, buildDoc, countBlocks, canAdd } from './program.js';
import { initialState, reduce, msgRun, msgStop, msgHello } from './carlink.js';

const $ = function (id) { return document.getElementById(id); };

const APP_KEY = 'bcc-app-v1';
const GRID_N = 6;
const START_POS = [0, 5, 'N'];
const OP_ICON = { fwd: 'i-fwd', back: 'i-back', left: 'i-left', right: 'i-right', repeat: 'i-rep', sound: 'i-sound', eye: 'i-eye' };
const OP_GROUP = { fwd: 'move', back: 'move', left: 'move', right: 'move', repeat: 'ctrl', sound: 'snd', eye: 'snd' };
const OP_NAME = { fwd: 'Tiến', back: 'Lùi', left: 'Quay trái', right: 'Quay phải', repeat: 'Lặp lại', sound: 'Âm thanh', eye: 'Đèn mắt' };
const EYE_COLORS = ['#E0453A', '#257A45', '#2F7BE0', '#F2B01E', '#8E55D6', '#16231D'];
const EYE_NAMES = ['Đỏ', 'Xanh lá', 'Xanh dương', 'Vàng', 'Tím', 'Tắt'];
const DIR_DEG = { N: 0, E: 90, S: 180, W: 270 };
const ERR_TEXT = {
  bad_json: 'Chương trình bị hỏng',
  bad_version: 'Sai phiên bản chương trình',
  empty: 'Dải lệnh đang trống',
  bad_op: 'Có khối không dùng được',
  bad_arg: 'Số trên khối chưa đúng',
  dup_id: 'Khối bị trùng mã',
  empty_repeat: 'Khung Lặp cần ít nhất 1 khối',
  nested_repeat: 'Không được lặp trong lặp',
  too_many_blocks: 'Nhiều khối quá',
  busy: 'Xe đang chạy',
  batt_low: 'Pin yếu, cần sạc',
  bad_msg: 'Xe không hiểu lệnh',
  edge: 'Xe chạm mép lưới',
  disc: 'Mất kết nối xe'
};

const elConn = $('conn');
const elDot = $('conn-dot');
const elName = $('conn-name');
const elBatt = $('batt');
const elTry = $('btn-try');
const elReal = $('btn-real');
const elStop = $('btn-stop');
const elGrid = $('grid');
const elStrip = $('strip');
const elPalette = $('palette');
const elStart = $('start-block');
const elPop = $('popover');
const elModal = $('modal');
const elToast = $('toast');
const elToastText = $('toast-text');
const elFile = $('file-input');

const elCells = [];
let carEl = null;
let carTurn = null;
let eyeEls = [];

let level = 1;
let strip = [];
let goal = [3, 2];
let uidSeq = 1;
let car = initialState();
let linkState = 'off';
let ws = null;
let wsUrl = '';
let wsWanted = false;
let wsRetry = null;
let lastFileName = 'robot-do';
let anim = { token: 0, running: false, real: false };
let realRun = null;
let press = null;
let popTarget = null;
let modalOpt = null;
let toastTimer = null;
let actx = null;

function makeUid() {
  uidSeq += 1;
  return 'u' + uidSeq;
}

function newBlock(op) {
  const blk = { uid: makeUid(), op: op };
  if (op === 'fwd' || op === 'back') {
    blk.n = 1;
  } else if (op === 'sound' || op === 'eye') {
    blk.n = 0;
  } else if (op === 'repeat') {
    blk.n = 2;
    blk.body = [];
  }
  return blk;
}

function findBlock(uid) {
  for (const blk of strip) {
    if (blk.uid === uid) {
      return blk;
    }
    if (blk.op === 'repeat' && Array.isArray(blk.body)) {
      for (const b of blk.body) {
        if (b.uid === uid) {
          return b;
        }
      }
    }
  }
  return null;
}

function elByUid(uid) {
  if (!uid) {
    return null;
  }
  return elStrip.querySelector('[data-uid="' + uid + '"]');
}

function plainBlock(blk) {
  const out = { op: blk.op };
  if (blk.n !== undefined) {
    out.n = blk.n;
  }
  if (blk.op === 'repeat') {
    out.body = (blk.body || []).map(plainBlock);
  }
  return out;
}

function plainStrip(list) {
  return (list || []).map(plainBlock);
}

function clampInt(v, lo, hi, dflt) {
  const n = Number(v);
  if (!Number.isInteger(n)) {
    return dflt;
  }
  return Math.min(hi, Math.max(lo, n));
}

function sanitizeStrip(raw, lv) {
  const allowed = LEVELS[lv].ops;
  const out = [];
  for (const b of raw) {
    if (!b || typeof b !== 'object') {
      continue;
    }
    const op = b.op;
    if (allowed.indexOf(op) === -1) {
      continue;
    }
    const nb = { uid: makeUid(), op: op };
    if (op === 'fwd' || op === 'back') {
      nb.n = clampInt(b.n, 1, 4, 1);
    } else if (op === 'sound') {
      nb.n = clampInt(b.n, 0, 2, 0);
    } else if (op === 'eye') {
      nb.n = clampInt(b.n, 0, 5, 0);
    } else if (op === 'repeat') {
      nb.n = clampInt(b.n, 2, 4, 2);
      nb.body = [];
      const body = Array.isArray(b.body) ? b.body : [];
      for (const c of body) {
        if (!c || typeof c !== 'object' || c.op === 'repeat' || allowed.indexOf(c.op) === -1) {
          continue;
        }
        const cc = { uid: makeUid(), op: c.op };
        if (cc.op === 'fwd' || cc.op === 'back') {
          cc.n = clampInt(c.n, 1, 4, 1);
        } else if (cc.op === 'sound') {
          cc.n = clampInt(c.n, 0, 2, 0);
        } else if (cc.op === 'eye') {
          cc.n = clampInt(c.n, 0, 5, 0);
        }
        nb.body.push(cc);
        if (nb.body.length >= 6) {
          break;
        }
      }
    }
    const addCount = 1 + (nb.op === 'repeat' ? nb.body.length : 0);
    if (countBlocks(out) + addCount > LEVELS[lv].maxBlocks) {
      continue;
    }
    out.push(nb);
  }
  return out;
}

function save() {
  try {
    localStorage.setItem(APP_KEY, JSON.stringify({ level: level, strip: plainStrip(strip) }));
  } catch (e) {
    // private mode: ignore
  }
}

function loadSaved() {
  try {
    const raw = localStorage.getItem(APP_KEY);
    if (!raw) {
      return;
    }
    const data = JSON.parse(raw);
    if (data && LEVELS[data.level]) {
      level = Number(data.level);
    }
    if (data && Array.isArray(data.strip)) {
      strip = sanitizeStrip(data.strip, level);
    }
  } catch (e) {
    level = 1;
    strip = [];
  }
}

function buildGrid() {
  elGrid.textContent = '';
  elCells.length = 0;
  for (let y = 0; y < GRID_N; y += 1) {
    for (let x = 0; x < GRID_N; x += 1) {
      const c = document.createElement('div');
      c.className = 'cell' + ((x + y) % 2 ? ' d' : '');
      c.dataset.x = String(x);
      c.dataset.y = String(y);
      elGrid.appendChild(c);
      elCells.push(c);
    }
  }
  carEl = document.createElement('div');
  carEl.className = 'car';
  carEl.innerHTML = '<div class="car-turn"><svg viewBox="0 0 64 64"><use href="#i-car"/></svg><span class="eye e1"></span><span class="eye e2"></span></div>';
  elGrid.appendChild(carEl);
  carTurn = carEl.querySelector('.car-turn');
  eyeEls = Array.prototype.slice.call(carEl.querySelectorAll('.eye'));
}

function cellAt(x, y) {
  if (x < 0 || x >= GRID_N || y < 0 || y >= GRID_N) {
    return null;
  }
  return elCells[y * GRID_N + x];
}

function paintGoal() {
  for (const c of elCells) {
    c.classList.remove('goal');
    c.innerHTML = '';
  }
  const c = cellAt(goal[0], goal[1]);
  if (c) {
    c.classList.add('goal');
    c.innerHTML = '<svg viewBox="0 0 64 64"><use href="#i-star"/></svg>';
  }
}

function placeCar(pos, smooth, durMove) {
  if (!carEl || !carTurn) {
    return;
  }
  const turn = DIR_DEG[pos[2]] || 0;
  const move = Math.max(0, durMove || 0);
  if (!smooth) {
    carEl.style.transition = 'none';
    carTurn.style.transition = 'none';
  } else {
    carEl.style.transition = 'left ' + move + 'ms linear, top ' + move + 'ms linear';
    carTurn.style.transition = 'transform ' + Math.min(400, Math.max(120, move)) + 'ms ease';
  }
  carEl.style.left = (pos[0] * (100 / GRID_N)) + '%';
  carEl.style.top = (pos[1] * (100 / GRID_N)) + '%';
  carTurn.style.transform = 'rotate(' + turn + 'deg)';
  if (!smooth) {
    void carEl.offsetWidth;
    carEl.style.transition = '';
    carTurn.style.transition = '';
  }
}

function resetCar() {
  placeCar(START_POS, false, 0);
}

function setEyes(n) {
  const color = (n === null || n === undefined || n === 5) ? '#16231D' : (EYE_COLORS[n] || '#16231D');
  for (const e of eyeEls) {
    e.style.background = color;
  }
}

function arrEl() {
  const s = document.createElement('span');
  s.className = 'arr';
  s.innerHTML = '<svg viewBox="0 0 24 24"><use href="#i-arr"/></svg>';
  return s;
}

function makeBlockEl(op) {
  const b = document.createElement('div');
  b.className = 'blk ' + OP_GROUP[op];
  b.dataset.op = op;
  b.title = OP_NAME[op];
  b.innerHTML = '<svg viewBox="0 0 64 64"><use href="#' + OP_ICON[op] + '"/></svg>';
  return b;
}

function addBadge(el, text, eyeColor) {
  const s = document.createElement('span');
  s.className = 'badge' + (eyeColor ? ' eyedot' : '');
  if (eyeColor) {
    s.style.background = eyeColor;
  } else {
    s.textContent = text;
  }
  el.appendChild(s);
}

function decorateBlock(blk, el) {
  if (blk.op === 'fwd' || blk.op === 'back') {
    if (LEVELS[level].counts) {
      addBadge(el, String(blk.n || 1), null);
    }
  } else if (blk.op === 'sound') {
    addBadge(el, String((blk.n || 0) + 1), null);
  } else if (blk.op === 'eye') {
    addBadge(el, '', (blk.n === 5 ? '#9AA7A1' : (EYE_COLORS[blk.n] || EYE_COLORS[0])));
  }
}

function renderItem(blk) {
  if (blk.op === 'repeat') {
    const frame = document.createElement('div');
    frame.className = 'rep';
    frame.dataset.uid = blk.uid;
    frame.dataset.op = 'repeat';
    const lab = document.createElement('button');
    lab.type = 'button';
    lab.className = 'lab';
    lab.textContent = '×' + (blk.n || 2);
    lab.title = OP_NAME.repeat;
    frame.appendChild(lab);
    const body = document.createElement('div');
    body.className = 'body';
    body.dataset.parent = blk.uid;
    for (const b of (blk.body || [])) {
      const be = makeBlockEl(b.op);
      be.dataset.uid = b.uid;
      decorateBlock(b, be);
      body.appendChild(be);
    }
    frame.appendChild(body);
    return frame;
  }
  const el = makeBlockEl(blk.op);
  el.dataset.uid = blk.uid;
  decorateBlock(blk, el);
  return el;
}

function assignIds() {
  let seq = 0;
  function walk(blk) {
    const el = elByUid(blk.uid);
    if (el) {
      el.dataset.id = String(seq);
    }
    seq += 1;
    if (blk.op === 'repeat' && Array.isArray(blk.body)) {
      for (const b of blk.body) {
        walk(b);
      }
    }
  }
  for (const blk of strip) {
    walk(blk);
  }
}

function renderStrip() {
  const kids = Array.prototype.slice.call(elStrip.children);
  for (const ch of kids) {
    if (ch !== elStart) {
      ch.remove();
    }
  }
  for (const blk of strip) {
    elStrip.appendChild(arrEl());
    elStrip.appendChild(renderItem(blk));
  }
  assignIds();
  refreshPaletteState();
  updateButtons();
}

function renderPalette() {
  elPalette.textContent = '';
  const groups = [
    ['move', ['fwd', 'back', 'left', 'right']],
    ['ctrl', ['repeat']],
    ['snd', ['sound', 'eye']]
  ];
  const allowed = LEVELS[level].ops;
  for (const g of groups) {
    const ops = g[1].filter(function (op) { return allowed.indexOf(op) !== -1; });
    if (!ops.length) {
      continue;
    }
    const box = document.createElement('div');
    box.className = 'grp ' + g[0];
    for (const op of ops) {
      const b = makeBlockEl(op);
      b.dataset.pal = '1';
      box.appendChild(b);
    }
    elPalette.appendChild(box);
  }
  refreshPaletteState();
}

function refreshPaletteState() {
  const blocks = elPalette.querySelectorAll('[data-pal]');
  for (const b of blocks) {
    if (canAdd(strip, b.dataset.op, level, false)) {
      b.classList.remove('off');
    } else {
      b.classList.add('off');
    }
  }
}

function renderLevels() {
  for (let i = 1; i <= 3; i += 1) {
    const b = $('level-' + i);
    if (i === level) {
      b.classList.add('on');
    } else {
      b.classList.remove('on');
    }
  }
}

function renderConn() {
  const online = linkState === 'on';
  elDot.className = 'dot ' + (online ? 'on' : (linkState === 'wait' ? 'wait' : 'off'));
  if (online) {
    elName.textContent = car.name || 'Xe';
  } else if (linkState === 'wait') {
    elName.textContent = 'Đang nối…';
  } else {
    elName.textContent = 'Chưa có xe';
  }
  if (car.color) {
    document.documentElement.style.setProperty('--car', car.color);
  }
  if (online && car.battMv !== null && car.battMv !== undefined) {
    elBatt.classList.remove('hidden');
    if (car.battMv < 4400) {
      elBatt.classList.add('warn');
    } else {
      elBatt.classList.remove('warn');
    }
    elBatt.title = 'Pin ' + car.battMv + ' mV';
  } else {
    elBatt.classList.add('hidden');
    elBatt.classList.remove('warn');
  }
}

function currentRun() {
  const doc = buildDoc(strip);
  const r = expand(doc);
  if (!r.ok) {
    return { ok: false, code: r.code, doc: doc };
  }
  return { ok: true, doc: doc, steps: r.steps, sim: simulate(r.steps) };
}

function updateButtons() {
  const r = currentRun();
  const canReal = car.connected && !car.running && !anim.running && r.ok && r.sim.edge === null;
  elReal.disabled = !canReal;
  elReal.title = canReal ? 'Gửi chương trình cho xe thật' : 'Cần nối xe và chương trình không chạm mép';
}

function setActive(id) {
  const running = elStrip.querySelectorAll('.run');
  for (const e of running) {
    e.classList.remove('run');
  }
  if (id === null || id === undefined) {
    return;
  }
  const el = elStrip.querySelector('[data-id="' + id + '"]');
  if (el) {
    el.classList.add('run');
  }
}

function showToast(text, warn) {
  elToastText.textContent = text;
  elToast.classList.remove('hidden');
  if (warn) {
    elToast.classList.add('warn');
  } else {
    elToast.classList.remove('warn');
  }
  if (toastTimer) {
    clearTimeout(toastTimer);
  }
  toastTimer = setTimeout(function () {
    elToast.classList.add('hidden');
  }, 3600);
}

function showRunError(code) {
  showToast(ERR_TEXT[code] || 'Chương trình chưa đúng', true);
  if (code === 'empty_repeat') {
    const frames = elStrip.querySelectorAll('.rep');
    for (const f of frames) {
      f.classList.add('err');
      setTimeout(function () { f.classList.remove('err'); }, 2200);
    }
  }
}

function wait(ms) {
  return new Promise(function (resolve) {
    setTimeout(resolve, ms);
  });
}

function audioCtx() {
  if (!actx) {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) {
      return null;
    }
    actx = new Ctx();
  }
  if (actx.state === 'suspended') {
    actx.resume();
  }
  return actx;
}

function tone(freq, start, dur, type, gain) {
  const ctx = audioCtx();
  if (!ctx) {
    return;
  }
  const t0 = ctx.currentTime + start;
  const osc = ctx.createOscillator();
  const g = ctx.createGain();
  osc.type = type || 'sine';
  osc.frequency.setValueAtTime(freq, t0);
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.linearRampToValueAtTime(gain || 0.06, t0 + 0.02);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  osc.connect(g).connect(ctx.destination);
  osc.start(t0);
  osc.stop(t0 + dur + 0.03);
}

function playSound(n) {
  if (n === 1) {
    tone(440, 0, 0.18, 'sawtooth', 0.05);
    tone(330, 0.18, 0.2, 'sawtooth', 0.05);
  } else if (n === 2) {
    tone(523, 0, 0.16, 'triangle', 0.06);
    tone(659, 0.16, 0.16, 'triangle', 0.06);
    tone(784, 0.32, 0.16, 'triangle', 0.06);
    tone(1047, 0.48, 0.3, 'triangle', 0.06);
  } else {
    tone(880, 0, 0.14, 'square', 0.045);
  }
}

function celebrate() {
  playSound(2);
  tone(1319, 0.62, 0.35, 'triangle', 0.06);
  elGrid.classList.add('celebrate');
  setTimeout(function () {
    elGrid.classList.remove('celebrate');
  }, 3000);
}

function speak(text) {
  try {
    const synth = window.speechSynthesis;
    if (!synth) {
      return;
    }
    const voices = synth.getVoices() || [];
    let viVoice = null;
    for (const v of voices) {
      if (v.lang && v.lang.toLowerCase().indexOf('vi') === 0) {
        viVoice = v;
        break;
      }
    }
    if (!viVoice) {
      return;
    }
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.voice = viVoice;
    u.lang = viVoice.lang || 'vi-VN';
    u.rate = 0.9;
    u.pitch = 1.05;
    u.volume = 1;
    synth.speak(u);
  } catch (e) {
    // no TTS: silent
  }
}

function cancelLocal() {
  anim.token += 1;
  anim.running = false;
  anim.real = false;
  realRun = null;
  if (anim.guard) {
    clearTimeout(anim.guard);
    anim.guard = null;
  }
  setActive(null);
}

function stopAll() {
  cancelLocal();
  if (ws && ws.readyState === 1) {
    try {
      ws.send(msgStop());
    } catch (e) {
      // ignore
    }
  }
  updateButtons();
}

async function animateTry(steps, sim) {
  anim.token += 1;
  const token = anim.token;
  anim.running = true;
  anim.real = false;
  resetCar();
  setEyes(null);
  setActive(null);
  let prev = START_POS.slice();
  for (let i = 0; i < steps.length; i += 1) {
    if (token !== anim.token) {
      return;
    }
    const id = steps[i][0];
    const op = steps[i][1];
    const arg = steps[i][2];
    const pos = sim.trace[i];
    setActive(id);
    if (op === 'fwd' || op === 'back') {
      const dist = Math.abs(pos[0] - prev[0]) + Math.abs(pos[1] - prev[1]);
      const dur = Math.max(1, dist) * 600;
      placeCar(pos, true, dur);
      await wait(dur);
    } else if (op === 'left' || op === 'right') {
      placeCar(pos, true, 400);
      await wait(400);
    } else if (op === 'sound') {
      playSound(arg);
      await wait(650);
    } else if (op === 'eye') {
      setEyes(arg);
      await wait(500);
    } else {
      await wait(450);
    }
    prev = pos;
    if (token !== anim.token) {
      return;
    }
  }
  anim.running = false;
  setActive(null);
  if (sim.edge !== null) {
    const badCell = cellAt(sim.final[0], sim.final[1]);
    if (badCell) {
      badCell.classList.add('edge');
      setTimeout(function () { badCell.classList.remove('edge'); }, 2400);
    }
    const badBlock = elStrip.querySelector('[data-id="' + sim.edge + '"]');
    if (badBlock) {
      badBlock.classList.add('err');
      setTimeout(function () { badBlock.classList.remove('err'); }, 2400);
    }
    showToast(ERR_TEXT.edge, true);
    updateButtons();
    return;
  }
  if (sim.final[0] === goal[0] && sim.final[1] === goal[1]) {
    celebrate();
  }
  updateButtons();
}

function runTry() {
  if (car.running || anim.real) {
    showToast('Xe đang chạy. Bấm DỪNG trước.', true);
    return;
  }
  cancelLocal();
  const r = currentRun();
  if (!r.ok) {
    showRunError(r.code);
    return;
  }
  animateTry(r.steps, r.sim);
}

function runReal() {
  if (elReal.disabled) {
    return;
  }
  const r = currentRun();
  if (!r.ok) {
    showRunError(r.code);
    return;
  }
  if (r.sim.edge !== null) {
    showToast('Chương trình chạm mép, chỉ chạy thử được.', true);
    return;
  }
  if (!car.connected || !ws || ws.readyState !== 1) {
    showToast(ERR_TEXT.disc, true);
    return;
  }
  cancelLocal();
  realRun = { trace: r.sim.trace, steps: r.steps, sim: r.sim };
  anim.running = true;
  anim.real = true;
  resetCar();
  setEyes(null);
  setActive(null);
  try {
    ws.send(msgRun(r.doc));
  } catch (e) {
    showToast('Không gửi được lệnh cho xe.', true);
    cancelLocal();
    updateButtons();
    return;
  }
  const guard = setTimeout(function () {
    if (anim.real && !car.running) {
      cancelLocal();
      updateButtons();
    }
  }, 6000);
  anim.guard = guard;
  updateButtons();
}

function beginRealRun() {
  if (!anim.real) {
    return;
  }
  resetCar();
  setEyes(null);
  setActive(null);
}

function onRealStep(msg) {
  if (!anim.real || !anim.running || !realRun) {
    return;
  }
  setActive(msg.id);
  const step = realRun.steps[msg.i];
  if (step) {
    if (step[1] === 'sound') {
      playSound(step[2]);
    } else if (step[1] === 'eye') {
      setEyes(step[2]);
    }
  }
  const pos = realRun.trace[msg.i];
  if (pos) {
    placeCar(pos, true, 600);
  }
}

function finishRealRun(success) {
  const run = realRun;
  if (anim.guard) {
    clearTimeout(anim.guard);
    anim.guard = null;
  }
  anim.running = false;
  anim.real = false;
  realRun = null;
  setActive(null);
  if (success && run) {
    placeCar(run.sim.final, true, 300);
    if (run.sim.final[0] === goal[0] && run.sim.final[1] === goal[1]) {
      celebrate();
    }
  }
  updateButtons();
}

function onWsMessage(text) {
  let msg = null;
  try {
    msg = JSON.parse(text);
  } catch (e) {
    return;
  }
  if (!msg || typeof msg.t !== 'string') {
    return;
  }
  if (msg.t === 'hello') {
    linkState = 'on';
  } else if (msg.t === 'started') {
    beginRealRun();
  } else if (msg.t === 'step') {
    onRealStep(msg);
  } else if (msg.t === 'done') {
    car = reduce(car, msg);
    renderConn();
    finishRealRun(true);
    return;
  } else if (msg.t === 'stopped') {
    car = reduce(car, msg);
    renderConn();
    finishRealRun(false);
    return;
  } else if (msg.t === 'err') {
    car = reduce(car, msg);
    renderConn();
    showToast(msg.msg || ERR_TEXT[msg.code] || 'Xe báo lỗi', true);
    finishRealRun(false);
    return;
  }
  car = reduce(car, msg);
  renderConn();
  updateButtons();
}

function scheduleReconnect() {
  if (!wsWanted || !wsUrl) {
    return;
  }
  if (wsRetry) {
    clearTimeout(wsRetry);
  }
  wsRetry = setTimeout(function () {
    wsRetry = null;
    connectWs(wsUrl);
  }, 2000);
}

function connectWs(url) {
  if (!url) {
    return;
  }
  wsUrl = url;
  wsWanted = true;
  if (ws && (ws.readyState === 0 || ws.readyState === 1)) {
    return;
  }
  linkState = 'wait';
  renderConn();
  try {
    ws = new WebSocket(url);
  } catch (e) {
    ws = null;
    linkState = 'off';
    renderConn();
    scheduleReconnect();
    return;
  }
  ws.onopen = function () {
    if (ws) {
      try {
        ws.send(msgHello());
      } catch (e) {
        // ignore
      }
    }
  };
  ws.onmessage = function (ev) {
    onWsMessage(ev.data);
  };
  ws.onclose = function () {
    ws = null;
    linkState = 'off';
    car = reduce(car, { t: 'disconnected' });
    renderConn();
    finishRealRun(false);
    scheduleReconnect();
  };
  ws.onerror = function () {
    if (ws) {
      try {
        ws.close();
      } catch (e) {
        // ignore
      }
    }
  };
}

function pageWsUrl() {
  const proto = location.protocol === 'https:' ? 'wss://' : 'ws://';
  return proto + location.host + '/ws';
}

function openModal(opt) {
  modalOpt = opt;
  $('modal-use').setAttribute('href', opt.icon || '#i-warn');
  $('modal-title').textContent = opt.title || 'Chú ý';
  $('modal-text').textContent = opt.text || '';
  const body = $('modal-body');
  body.textContent = '';
  opt._input = null;
  if (opt.input) {
    const inp = document.createElement('input');
    inp.type = 'text';
    inp.value = opt.input.value || '';
    inp.placeholder = opt.input.placeholder || '';
    inp.maxLength = 40;
    body.appendChild(inp);
    opt._input = inp;
  }
  $('modal-ok').textContent = opt.okText || 'Đồng ý';
  $('modal-cancel').textContent = opt.cancelText || 'Hủy';
  if (opt.hideCancel) {
    $('modal-cancel').classList.add('hidden');
  } else {
    $('modal-cancel').classList.remove('hidden');
  }
  elModal.classList.remove('hidden');
  if (opt._input) {
    setTimeout(function () {
      opt._input.focus();
      opt._input.select();
    }, 60);
  }
}

function closeModal() {
  elModal.classList.add('hidden');
  modalOpt = null;
}

function closePop() {
  elPop.classList.add('hidden');
  popTarget = null;
}

function soundLabel(n) {
  return String(n + 1);
}

function popOption(text, isOn, handler) {
  const b = document.createElement('button');
  b.type = 'button';
  b.textContent = text;
  if (isOn) {
    b.classList.add('on');
  }
  b.addEventListener('click', function (ev) {
    ev.stopPropagation();
    handler();
    renderStrip();
    save();
    updateButtons();
    closePop();
  });
  return b;
}

function popEyeOption(n) {
  const b = document.createElement('button');
  b.type = 'button';
  b.className = 'swatch';
  b.style.background = n === 5 ? '#9AA7A1' : EYE_COLORS[n];
  b.title = EYE_NAMES[n];
  const current = popTarget && popTarget.n === n;
  if (current) {
    b.classList.add('on');
  }
  b.addEventListener('click', function (ev) {
    ev.stopPropagation();
    if (popTarget) {
      popTarget.n = n;
    }
    renderStrip();
    save();
    updateButtons();
    closePop();
  });
  return b;
}

function openChooser(blk, anchor) {
  closePop();
  if (!blk || !anchor) {
    return;
  }
  popTarget = blk;
  elPop.textContent = '';
  let count = 0;
  if (blk.op === 'fwd' || blk.op === 'back') {
    if (!LEVELS[level].counts) {
      popTarget = null;
      return;
    }
    for (let n = 1; n <= 4; n += 1) {
      elPop.appendChild(popOption(String(n), blk.n === n, (function (v) {
        return function () { if (popTarget) { popTarget.n = v; } };
      })(n)));
      count += 1;
    }
  } else if (blk.op === 'repeat') {
    for (let n = 2; n <= 4; n += 1) {
      elPop.appendChild(popOption('×' + n, blk.n === n, (function (v) {
        return function () { if (popTarget) { popTarget.n = v; } };
      })(n)));
      count += 1;
    }
  } else if (blk.op === 'sound') {
    for (let n = 0; n <= 2; n += 1) {
      elPop.appendChild(popOption(soundLabel(n), blk.n === n, (function (v) {
        return function () { if (popTarget) { popTarget.n = v; } };
      })(n)));
      count += 1;
    }
  } else if (blk.op === 'eye') {
    for (let n = 0; n < EYE_COLORS.length; n += 1) {
      elPop.appendChild(popEyeOption(n));
      count += 1;
    }
  }
  if (!count) {
    popTarget = null;
    return;
  }
  elPop.classList.remove('hidden');
  const rect = anchor.getBoundingClientRect();
  const half = (count * 64) / 2 + 20;
  const cx = Math.min(window.innerWidth - half, Math.max(half, rect.left + rect.width / 2));
  elPop.style.left = cx + 'px';
  elPop.style.top = Math.max(90, rect.top - 12) + 'px';
}

function refreshLevel(newLevel) {
  if (newLevel === level) {
    return;
  }
  const allowed = LEVELS[newLevel].ops;
  let removed = 0;
  const next = [];
  for (const blk of strip) {
    if (allowed.indexOf(blk.op) === -1) {
      removed += 1;
      continue;
    }
    if (blk.op === 'repeat') {
      const kept = (blk.body || []).filter(function (b) { return allowed.indexOf(b.op) !== -1; });
      removed += (blk.body || []).length - kept.length;
      const copy = { uid: blk.uid, op: 'repeat', n: blk.n, body: kept };
      next.push(copy);
    } else {
      next.push(blk);
    }
  }
  const apply = function () {
    level = newLevel;
    strip = next;
    renderLevels();
    renderPalette();
    renderStrip();
    save();
    updateButtons();
  };
  if (removed > 0) {
    openModal({
      icon: '#i-warn',
      title: 'Đổi cấp học',
      text: 'Cấp ' + newLevel + ' không có ' + removed + ' khối đang dùng. Bỏ các khối đó để đổi cấp?',
      okText: 'Đổi cấp',
      onOk: apply
    });
  } else {
    apply();
  }
}

function topInsertIndex(x, excludeUid) {
  const items = [];
  for (const ch of elStrip.children) {
    if (ch === elStart) {
      continue;
    }
    if (!ch.classList || (!ch.classList.contains('blk') && !ch.classList.contains('rep'))) {
      continue;
    }
    if (excludeUid && ch.dataset.uid === excludeUid) {
      continue;
    }
    items.push(ch);
  }
  let idx = 0;
  for (const it of items) {
    const r = it.getBoundingClientRect();
    if (x > r.left + r.width / 2) {
      idx += 1;
    } else {
      break;
    }
  }
  return idx;
}

function bodyInsertIndex(repEl, x, excludeUid) {
  const bodyEl = repEl.querySelector('.body');
  if (!bodyEl) {
    return 999;
  }
  let idx = 0;
  for (const ch of bodyEl.children) {
    if (excludeUid && ch.dataset.uid === excludeUid) {
      continue;
    }
    const r = ch.getBoundingClientRect();
    if (x > r.left + r.width / 2) {
      idx += 1;
    } else {
      break;
    }
  }
  return idx;
}

function removeBlock(uid) {
  for (let i = 0; i < strip.length; i += 1) {
    if (strip[i].uid === uid) {
      strip.splice(i, 1);
      return true;
    }
    if (strip[i].op === 'repeat' && Array.isArray(strip[i].body)) {
      const body = strip[i].body;
      for (let j = 0; j < body.length; j += 1) {
        if (body[j].uid === uid) {
          body.splice(j, 1);
          return true;
        }
      }
    }
  }
  return false;
}

function shakePalette(op) {
  const b = elPalette.querySelector('[data-op="' + op + '"]');
  if (!b) {
    return;
  }
  b.classList.remove('shake');
  void b.offsetWidth;
  b.classList.add('shake');
  setTimeout(function () { b.classList.remove('shake'); }, 420);
}

function addFromPalette(op, atIndex) {
  if (!canAdd(strip, op, level, false)) {
    shakePalette(op);
    return false;
  }
  const blk = newBlock(op);
  const idx = typeof atIndex === 'number' ? Math.min(atIndex, strip.length) : strip.length;
  strip.splice(idx, 0, blk);
  renderStrip();
  save();
  updateButtons();
  if (op === 'repeat' || ((op === 'fwd' || op === 'back') && LEVELS[level].counts)) {
    setTimeout(function () {
      const el = elByUid(blk.uid);
      if (el) {
        openChooser(blk, el);
      }
    }, 0);
  }
  return true;
}

function addIntoRepeat(repEl, op) {
  const parent = findBlock(repEl.dataset.uid);
  if (!parent || parent.op !== 'repeat') {
    return;
  }
  const body = parent.body || [];
  const allowed = LEVELS[level].ops.indexOf(op) !== -1;
  const tooMany = body.length + 1 > 6;
  const overMax = countBlocks(strip) + 1 > LEVELS[level].maxBlocks;
  if (op === 'repeat' || !allowed || tooMany || overMax) {
    shakePalette(op);
    return;
  }
  body.push(newBlock(op));
  parent.body = body;
  renderStrip();
  save();
  updateButtons();
}

function onBlockPointerDown(ev, info, sourceEl) {
  if (ev.button !== undefined && ev.button !== 0) {
    return;
  }
  closePop();
  if (ws && ws.readyState !== 1) {
    // still allow arranging locally
  }
  press = {
    info: info,
    el: sourceEl,
    x: ev.clientX,
    y: ev.clientY,
    moved: false,
    ghost: null,
    offX: 0,
    offY: 0,
    pointerId: ev.pointerId,
    timer: null
  };
  try {
    sourceEl.setPointerCapture(ev.pointerId);
  } catch (e) {
    // ignore
  }
  press.timer = setTimeout(function () {
    if (press && !press.moved) {
      speak(OP_NAME[press.info.op] || '');
    }
  }, 600);
  document.addEventListener('pointermove', onPointerMove);
  document.addEventListener('pointerup', onPointerUp);
  document.addEventListener('pointercancel', onPointerUp);
}

function onPointerMove(ev) {
  if (!press || ev.pointerId !== press.pointerId) {
    return;
  }
  const dx = ev.clientX - press.x;
  const dy = ev.clientY - press.y;
  if (!press.moved && (Math.abs(dx) > 8 || Math.abs(dy) > 8)) {
    press.moved = true;
    if (press.timer) {
      clearTimeout(press.timer);
    }
    startGhost();
  }
  if (!press.moved) {
    return;
  }
  if (ev.cancelable) {
    ev.preventDefault();
  }
  moveGhost(ev.clientX, ev.clientY);
  updateDropHint(ev.clientX, ev.clientY);
}

function startGhost() {
  if (!press) {
    return;
  }
  const rect = press.el.getBoundingClientRect();
  press.offX = press.x - rect.left;
  press.offY = press.y - rect.top;
  const g = press.el.cloneNode(true);
  g.classList.add('drag-ghost');
  g.classList.remove('run');
  g.style.width = rect.width + 'px';
  g.style.height = rect.height + 'px';
  g.style.left = rect.left + 'px';
  g.style.top = rect.top + 'px';
  document.body.appendChild(g);
  press.ghost = g;
  press.el.classList.add('dragging');
}

function moveGhost(x, y) {
  if (!press || !press.ghost) {
    return;
  }
  press.ghost.style.left = (x - press.offX) + 'px';
  press.ghost.style.top = (y - press.offY) + 'px';
}

function clearHints() {
  elStrip.classList.remove('over');
  const all = document.querySelectorAll('.over');
  for (const e of all) {
    e.classList.remove('over');
  }
}

function updateDropHint(x, y) {
  clearHints();
  const el = document.elementFromPoint(x, y);
  if (!el) {
    return;
  }
  if (el.closest('.body')) {
    const rep = el.closest('.rep');
    if (rep) {
      rep.classList.add('over');
    }
    return;
  }
  if (el.closest('#strip')) {
    elStrip.classList.add('over');
  }
}

function onPointerUp(ev) {
  if (!press || ev.pointerId !== press.pointerId) {
    return;
  }
  if (press.timer) {
    clearTimeout(press.timer);
  }
  document.removeEventListener('pointermove', onPointerMove);
  document.removeEventListener('pointerup', onPointerUp);
  document.removeEventListener('pointercancel', onPointerUp);
  const p = press;
  press = null;
  if (p.ghost) {
    p.ghost.remove();
  }
  if (p.el) {
    p.el.classList.remove('dragging');
  }
  clearHints();
  if (!p.moved) {
    handleTap(p.info);
    return;
  }
  handleDrop(p, ev.clientX, ev.clientY);
}

function handleTap(info) {
  if (!info) {
    return;
  }
  if (info.kind === 'palette') {
    const ok = addFromPalette(info.op, strip.length);
    if (ok) {
      audioCtx();
    }
    return;
  }
  const blk = findBlock(info.uid);
  const el = elByUid(info.uid);
  if (blk && el) {
    openChooser(blk, el);
  }
}

function handleDrop(p, x, y) {
  const el = document.elementFromPoint(x, y);
  if (!el) {
    if (p.info.kind === 'item') {
      removeBlock(p.info.uid);
    }
    renderStrip();
    save();
    return;
  }
  const repEl = el.closest('.rep');
  const bodyEl = el.closest('.body');
  const inStrip = !!el.closest('#strip');

  if (p.info.kind === 'palette') {
    if (repEl && bodyEl) {
      addIntoRepeat(repEl, p.info.op);
      return;
    }
    if (inStrip) {
      addFromPalette(p.info.op, topInsertIndex(x, null));
    }
    return;
  }

  const blk = findBlock(p.info.uid);
  if (!blk) {
    return;
  }

  if (repEl && bodyEl) {
    const target = findBlock(repEl.dataset.uid);
    if (!target || target.op !== 'repeat') {
      return;
    }
    if (blk.op === 'repeat') {
      showToast('Khung Lặp không lồng nhau.', true);
      return;
    }
    const inTarget = p.info.parent === target.uid;
    const before = (target.body || []).length;
    if (before - (inTarget ? 1 : 0) + 1 > 6) {
      showToast('Khung Lặp tối đa 6 khối.', true);
      return;
    }
    removeBlock(p.info.uid);
    target.body = target.body || [];
    const idx = bodyInsertIndex(repEl, x, p.info.uid);
    target.body.splice(Math.min(idx, target.body.length), 0, blk);
    renderStrip();
    save();
    updateButtons();
    return;
  }

  if (inStrip) {
    const idx = topInsertIndex(x, p.info.uid);
    removeBlock(p.info.uid);
    strip.splice(Math.min(idx, strip.length), 0, blk);
    renderStrip();
    save();
    updateButtons();
    return;
  }

  removeBlock(p.info.uid);
  renderStrip();
  save();
  updateButtons();
}

function exportFile() {
  const data = { v: 1, app: 'block-coding-car', level: level, strip: plainStrip(strip) };
  const text = JSON.stringify(data, null, 1);
  const blob = new Blob([text], { type: 'application/json' });
  const a = document.createElement('a');
  const url = URL.createObjectURL(blob);
  a.href = url;
  a.download = 'chuong-trinh-xe.json';
  document.body.appendChild(a);
  a.click();
  setTimeout(function () {
    URL.revokeObjectURL(url);
    a.remove();
  }, 1200);
}

function importText(text) {
  let data = null;
  try {
    data = JSON.parse(text);
  } catch (e) {
    showToast('Tệp không phải JSON hợp lệ.', true);
    return;
  }
  if (!data || typeof data !== 'object') {
    showToast('Tệp chương trình không đúng.', true);
    return;
  }
  let lv = Number(data.level);
  if (!LEVELS[lv]) {
    lv = level;
  }
  let raw = data.strip;
  if (!Array.isArray(raw) && Array.isArray(data.prog)) {
    raw = data.prog;
  }
  if (!Array.isArray(raw)) {
    showToast('Tệp không có dải lệnh.', true);
    return;
  }
  level = lv;
  strip = sanitizeStrip(raw, level);
  cancelLocal();
  renderLevels();
  renderPalette();
  renderStrip();
  save();
  updateButtons();
  showToast('Đã nhập chương trình.');
}

function bindUI() {
  elTry.addEventListener('click', function () {
    audioCtx();
    runTry();
  });
  elReal.addEventListener('click', function () {
    audioCtx();
    runReal();
  });
  elStop.addEventListener('click', function () {
    stopAll();
  });
  $('btn-clear').addEventListener('click', function () {
    stopAll();
    strip = [];
    renderStrip();
    save();
    updateButtons();
  });
  $('btn-export').addEventListener('click', exportFile);
  $('btn-import').addEventListener('click', function () {
    elFile.click();
  });
  elFile.addEventListener('change', function () {
    const f = elFile.files && elFile.files[0];
    if (!f) {
      return;
    }
    f.text().then(importText).catch(function () {
      showToast('Không đọc được tệp.', true);
    });
    elFile.value = '';
  });

  for (let i = 1; i <= 3; i += 1) {
    (function (lv) {
      $('level-' + lv).addEventListener('click', function () {
        refreshLevel(lv);
      });
    })(i);
  }

  elConn.addEventListener('click', function () {
    if (location.protocol === 'file:') {
      if (linkState === 'on') {
        showToast('Đang nối xe ' + (car.name || ''));
        return;
      }
      openModal({
        icon: '#i-car',
        title: 'Kết nối xe',
        text: 'Nhập tên xe trên mạng nhà (ví dụ: robot-do).',
        input: { value: lastFileName, placeholder: 'robot-do' },
        okText: 'Kết nối',
        onOk: function (value) {
          let name = String(value || '').trim().toLowerCase();
          name = name.replace(/^wss?:\/\//, '').replace(/\/.*$/, '').replace(/\.local$/, '');
          if (!/^[a-z0-9-]+$/.test(name)) {
            showToast('Tên xe chỉ gồm chữ, số và dấu gạch.', true);
            return;
          }
          lastFileName = name;
          connectWs('ws://' + name + '.local/ws');
        }
      });
    } else if (linkState === 'on') {
      showToast('Đang nối xe ' + (car.name || '') + ' · pin ' + (car.battMv || '?') + ' mV');
    } else {
      connectWs(pageWsUrl());
    }
  });

  elGrid.addEventListener('dblclick', function (ev) {
    const c = ev.target.closest('.cell');
    if (!c) {
      return;
    }
    goal = [Number(c.dataset.x), Number(c.dataset.y)];
    paintGoal();
    showToast('Đã dời ngôi sao.');
  });

  elPalette.addEventListener('pointerdown', function (ev) {
    const b = ev.target.closest('.blk');
    if (!b || !b.dataset.op) {
      return;
    }
    onBlockPointerDown(ev, { kind: 'palette', op: b.dataset.op }, b);
  });

  elStrip.addEventListener('pointerdown', function (ev) {
    if (ev.target.closest('#start-block')) {
      return;
    }
    const b = ev.target.closest('.blk');
    if (b && b.dataset.uid) {
      const bodyEl = b.closest('.body');
      onBlockPointerDown(ev, {
        kind: 'item',
        uid: b.dataset.uid,
        parent: bodyEl ? bodyEl.dataset.parent : null,
        op: b.dataset.op
      }, b);
      return;
    }
    const rep = ev.target.closest('.rep');
    if (rep && rep.dataset.uid) {
      onBlockPointerDown(ev, { kind: 'item', uid: rep.dataset.uid, parent: null, op: 'repeat' }, rep);
    }
  });

  document.addEventListener('contextmenu', function (ev) {
    if (ev.target.closest && ev.target.closest('.blk')) {
      ev.preventDefault();
    }
  });

  document.addEventListener('pointerdown', function (ev) {
    if (!elPop.classList.contains('hidden') && !ev.target.closest('#popover')) {
      closePop();
    }
  });

  $('modal-ok').addEventListener('click', function () {
    const opt = modalOpt;
    if (!opt) {
      return;
    }
    const value = opt._input ? opt._input.value : null;
    closeModal();
    if (opt.onOk) {
      opt.onOk(value);
    }
  });
  $('modal-cancel').addEventListener('click', function () {
    const opt = modalOpt;
    closeModal();
    if (opt && opt.onCancel) {
      opt.onCancel();
    }
  });
  elModal.addEventListener('click', function (ev) {
    if (ev.target === elModal) {
      closeModal();
    }
  });

  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') {
      closePop();
      if (!elModal.classList.contains('hidden')) {
        closeModal();
      }
    }
    if (ev.key === 'Enter' && !elModal.classList.contains('hidden') && modalOpt && modalOpt._input) {
      $('modal-ok').click();
    }
  });
}

function boot() {
  buildGrid();
  paintGoal();
  resetCar();
  setEyes(null);
  loadSaved();
  if (!LEVELS[level]) {
    level = 1;
  }
  renderLevels();
  renderPalette();
  renderStrip();
  renderConn();
  updateButtons();
  bindUI();
  if (location.protocol === 'http:' || location.protocol === 'https:') {
    connectWs(pageWsUrl());
  }
}

boot();
