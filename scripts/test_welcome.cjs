// Run with: node scripts/test_welcome.cjs (no npm dependencies).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('static/js/welcome.js', 'utf8');

function boot({returning = false, reduced = false, blocked = false, paused = false} = {}) {
  const events = {};
  const timers = new Map();
  const effects = [];
  const storage = new Map(returning ? [['warble-welcome-seen', '1']] : []);
  const root = {dataset: {}};
  const title = {focus() { this.focused = true; }};
  const element = () => ({children: [], style: {setProperty() {}},
    append(child) { this.children.push(child); }, setAttribute() {},
    remove() { this.removed = true; }});
  const world = {append(child) { effects.push(child); }};
  const context = {
    document: {documentElement: root, body: {dataset: {}},
      querySelector: s => ({'[data-welcome-hero]': {scrollIntoView() {}, querySelector() { return null; }}, '.world': world,
        '#standings-title': title})[s],
      createElement: element,
      addEventListener: (name, fn) => { events[name] = fn; }},
    window: {matchMedia: () => ({matches: reduced, addEventListener() {}})},
    localStorage: {
      getItem(k) {
        if (blocked) throw Error('Storage blocked');
        return k === 'warble-motion' && paused ? 'paused' : storage.get(k);
      },
      removeItem(k) { storage.delete(k); },
      setItem(k, v) { if (blocked) throw Error('Storage blocked'); storage.set(k, v); }
    },
    setTimeout(fn, delay) { const id = timers.size + 1; timers.set(id, {fn, delay}); return id; },
    clearTimeout(id) { timers.delete(id); },
    MutationObserver: class { observe() {} }
  };
  vm.runInNewContext(source, context);
  events.DOMContentLoaded();
  return {root, events, timers, effects, title, storage};
}

for (const options of [{}, {blocked: true}]) {
  const run = boot(options);
  assert.equal(run.root.dataset.welcomeScene, 'active');
  assert.equal(run.effects[0].children.length, 30);
  assert.equal([...run.timers.values()][0].delay, 7000);
  [...run.timers.values()][0].fn();
  assert.equal(run.root.dataset.welcome, 'seen');
  assert.equal(run.root.dataset.welcomeScene, undefined);
  assert.equal(run.effects[0].removed, true);
  run.events['htmx:afterSwap']();
  assert.equal(run.effects.length, 1);
}
for (const options of [{returning: true}, {reduced: true}, {paused: true}]) {
  const run = boot(options);
  assert.equal(run.root.dataset.welcome, 'seen');
  assert.equal(run.effects.length, 0);
  assert.equal(run.timers.size, 0);
}
for (const event of ['keydown', 'click']) {
  const run = boot();
  run.events[event]({key: 'Escape', target: {closest: selector => selector.includes('welcome-skip')}});
  assert.equal(run.effects[0].removed, true);
  assert.equal(run.title.focused, true);
  assert.equal([...run.timers.values()].some(timer => timer.delay === 7000), false);
}
console.log('Welcome checks passed: first visit, seven-second timer, repeat visit, skip, reduced motion, paused motion, unavailable storage, HTMX.');

const replay = boot({returning: true});
replay.events.click({target: {closest: selector => selector === '[data-welcome-reset]'}, preventDefault() {}});
assert.equal(replay.root.dataset.welcomeScene, 'active');
assert.equal(replay.effects.length, 1);
