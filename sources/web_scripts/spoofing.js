/*
 * AgenticSeek identity-consistent browser spoof.
 *
 * Injection contract: a `const __IDENTITY__ = {...};` binding is prepended to
 * this file by the Python side (CDP Page.addScriptToEvaluateOnNewDocument),
 * making the whole payload one classic script. The binding is script-scoped,
 * so nothing leaks onto `window` for page scripts to find.
 *
 * Design rules (each one fixes a concrete detection vector):
 *  1. every override is a Proxy around the native function it replaces, so
 *     it keeps the native name, length, missing `prototype` and
 *     "is not a constructor" behaviour. Plain wrapper functions failed all
 *     of these checks.
 *  2. the native getter still runs first, so a bad receiver throws the real
 *     "Illegal invocation"; our trap frames are removed from that stack.
 *  3. Function.prototype.toString is proxied too and prints the native
 *     source of every override.
 *  4. values are stable: same question, same answer, forever.
 *  5. spoof only what Web Workers cannot contradict. Workers run without
 *     this script, so canvas, WebGL, platform, hardwareConcurrency and
 *     deviceMemory stay real. Client hints come from the CDP user-agent
 *     override, which reaches workers and HTTP headers as well.
 *
 * Cross-realm: each same-origin frame runs this script too. When one realm's
 * toString meets another realm's proxy, it finds the proxy among that
 * realm's overridden getters and prints the same native source.
 */
(() => {
  'use strict';

  const I = (typeof __IDENTITY__ !== 'undefined') ? __IDENTITY__ : null;
  if (!I) { return; }

  // ------------------------------------------------------------- infrastructure
  const nativeToString = Function.prototype.toString;
  const reflectApply = Reflect.apply;
  const getDescriptor = Object.getOwnPropertyDescriptor;
  const nativeSource = new WeakMap();
  // What V8 prints for any Proxy of a function, whatever its name.
  const ANONYMOUS_NATIVE = 'function () { [native code] }';
  // Frames our traps add to a stack trace (page frames never start this way).
  const TRAP_FRAME_PREFIXES = ['at Reflect.apply (<anonymous>)', 'at Object.apply (<anonymous>:'];
  // [interface, property] for every getter this script overrides.
  const overriddenGetters = [];

  function hideTrapFrames(error) {
    try {
      if (error && typeof error.stack === 'string') {
        error.stack = error.stack.split('\n')
          .filter((line) => !TRAP_FRAME_PREFIXES.some((prefix) => line.trim().startsWith(prefix)))
          .join('\n');
      }
    } catch (e) {}
    return error;
  }

  // Proxy a native function. `override(realResult)` gives the spoofed result.
  function proxyNative(original, override) {
    const proxy = new Proxy(original, {
      apply(target, thisArg, args) {
        let real;
        try {
          real = reflectApply(target, thisArg, args);
        } catch (error) {
          throw hideTrapFrames(error);
        }
        return override(real);
      },
    });
    nativeSource.set(proxy, reflectApply(nativeToString, original, []));
    return proxy;
  }

  // Swap an interface getter for a proxy, keeping the native descriptor shape.
  function overrideGetter(interfaceName, name, value) {
    try {
      const proto = window[interfaceName].prototype;
      const descriptor = getDescriptor(proto, name);
      if (!descriptor || typeof descriptor.get !== 'function') { return; }
      descriptor.get = proxyNative(descriptor.get, () => value);
      Object.defineProperty(proto, name, descriptor);
      overriddenGetters.push([interfaceName, name]);
    } catch (e) {}
  }

  // Every same-origin window reachable from the top, this one included.
  function sameOriginRealms() {
    const realms = [];
    const visit = (win) => {
      try {
        if (realms.indexOf(win) !== -1 || typeof win.Function !== 'function') { return; }
      } catch (e) { return; } // cross-origin frame
      realms.push(win);
      for (let i = 0; i < win.frames.length; i++) { visit(win.frames[i]); }
    };
    visit(window.top);
    visit(window);
    return realms;
  }

  // Native source of a proxy that another realm's copy of this script made.
  function foreignNativeSource(fn) {
    for (const realm of sameOriginRealms()) {
      if (realm === window) { continue; }
      try {
        if (fn === realm.Function.prototype.toString) { return 'function toString() { [native code] }'; }
        for (const [interfaceName, name] of overriddenGetters) {
          const descriptor = getDescriptor(realm[interfaceName].prototype, name);
          if (descriptor && descriptor.get === fn) { return 'function get ' + name + '() { [native code] }'; }
        }
      } catch (e) {}
    }
    return undefined;
  }

  try {
    const toStringProxy = new Proxy(nativeToString, {
      apply(target, thisArg, args) {
        const source = nativeSource.get(thisArg);
        if (source !== undefined) { return source; }
        let real;
        try {
          real = reflectApply(target, thisArg, args);
        } catch (error) {
          throw hideTrapFrames(error);
        }
        return (real === ANONYMOUS_NATIVE && foreignNativeSource(thisArg)) || real;
      },
    });
    nativeSource.set(toStringProxy, reflectApply(nativeToString, nativeToString, []));
    Object.defineProperty(Function.prototype, 'toString', {
      value: toStringProxy, writable: true, configurable: true, enumerable: false,
    });
  } catch (e) {}

  // ------------------------------------------------------- chromedriver residue
  // cdc_ variable names change across chromedriver builds: match the prefix,
  // not one hardcoded historical name.
  try {
    for (const holder of [window, document]) {
      for (const key of Object.getOwnPropertyNames(holder)) {
        if (key.startsWith('cdc_') || key.startsWith('$cdc_')) {
          try { delete holder[key]; } catch (e) {}
        }
      }
    }
  } catch (e) {}

  // ------------------------------------------------------------------ navigator
  // Real Chrome returns one frozen array until the languages change.
  if (Array.isArray(I.navigator && I.navigator.languages)) {
    overrideGetter('Navigator', 'languages', Object.freeze(I.navigator.languages.slice()));
  }

  // --------------------------------------------------------------------- screen
  // Patch individual properties on Screen.prototype so unknown/future
  // properties (orientation, isExtended) stay real.
  if (typeof Screen !== 'undefined' && I.screen) {
    const screenValues = {
      width: I.screen.width,
      height: I.screen.height,
      availWidth: I.screen.avail_width,
      availHeight: I.screen.avail_height,
      availLeft: I.screen.avail_left,
      availTop: I.screen.avail_top,
      colorDepth: 24,
      pixelDepth: 24,
    };
    for (const key of Object.keys(screenValues)) {
      overrideGetter('Screen', key, screenValues[key]);
    }
  }

  // Intentionally NOT spoofed (each was a detection vector before):
  //   navigator.webdriver / vendor (already real-false / "Google Inc."),
  //   userAgentData (CDP override serves the native object), plugins,
  //   canvas, WebGL, RTCPeerConnection, Notification, document.fonts,
  //   AudioContext, performance.memory.
})();
