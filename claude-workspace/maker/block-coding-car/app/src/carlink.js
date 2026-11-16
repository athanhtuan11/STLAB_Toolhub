// carlink.js - pure state machine for the car WebSocket + outgoing messages.

export function initialState() {
  return {
    connected: false,
    name: '',
    color: '#E0453A',
    fw: '',
    battMv: null,
    busy: false,
    running: false,
    activeId: null,
    stepIndex: null,
    stopWhy: null,
    lastError: null,
    stepsCell: null,
    steps90: null
  };
}

export function reduce(state, msg) {
  if (!msg || typeof msg !== 'object') {
    return state;
  }
  const t = msg.t;
  if (t === 'hello') {
    const s = Object.assign({}, state);
    s.connected = true;
    s.name = typeof msg.name === 'string' ? msg.name : state.name;
    s.color = typeof msg.color === 'string' ? msg.color : state.color;
    s.fw = typeof msg.fw === 'string' ? msg.fw : state.fw;
    s.battMv = typeof msg.batt_mv === 'number' ? msg.batt_mv : state.battMv;
    s.busy = !!msg.busy;
    if (typeof msg.steps_cell === 'number') {
      s.stepsCell = msg.steps_cell;
    }
    if (typeof msg.steps_90 === 'number') {
      s.steps90 = msg.steps_90;
    }
    return s;
  }
  if (t === 'started') {
    const s = Object.assign({}, state);
    s.running = true;
    s.busy = true;
    s.activeId = null;
    s.stepIndex = -1;
    s.stopWhy = null;
    s.lastError = null;
    return s;
  }
  if (t === 'step') {
    const s = Object.assign({}, state);
    s.running = true;
    s.busy = true;
    s.activeId = typeof msg.id === 'number' ? msg.id : null;
    s.stepIndex = typeof msg.i === 'number' ? msg.i : s.stepIndex;
    return s;
  }
  if (t === 'done') {
    const s = Object.assign({}, state);
    s.running = false;
    s.busy = false;
    s.activeId = null;
    return s;
  }
  if (t === 'stopped') {
    const s = Object.assign({}, state);
    s.running = false;
    s.busy = false;
    s.activeId = null;
    s.stopWhy = typeof msg.why === 'string' ? msg.why : 'client';
    return s;
  }
  if (t === 'err') {
    const s = Object.assign({}, state);
    s.lastError = typeof msg.code === 'string' ? msg.code : 'bad_msg';
    s.running = false;
    s.busy = false;
    s.activeId = null;
    return s;
  }
  if (t === 'batt') {
    const s = Object.assign({}, state);
    if (typeof msg.mv === 'number') {
      s.battMv = msg.mv;
    }
    return s;
  }
  if (t === 'connecting') {
    const s = Object.assign({}, state);
    s.connected = false;
    return s;
  }
  if (t === 'disconnected') {
    const s = Object.assign({}, state);
    s.connected = false;
    s.busy = false;
    s.running = false;
    s.activeId = null;
    return s;
  }
  return state;
}

export function msgRun(doc) {
  return JSON.stringify({ t: 'run', prog: doc.prog });
}

export function msgStop() {
  return JSON.stringify({ t: 'stop' });
}

export function msgHello() {
  return JSON.stringify({ t: 'hello' });
}
