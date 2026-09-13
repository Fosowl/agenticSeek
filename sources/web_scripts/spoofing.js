/*
 * AgenticSeek identity-consistent browser spoof.
 *
 * Injection contract: a `const __IDENTITY__ = {...};` binding is prepended to
 * this file by the Python side (CDP Page.addScriptToEvaluateOnNewDocument),
 * making the whole payload one classic script. The binding is script-scoped,
 * so nothing leaks onto `window` for page scripts to find.
 *
 * Design rules (each one fixes a concrete detection vector):
 *  1. capture the original function before overriding, and always delegate
 *     back to it in a try/catch - overrides must never throw where real
 *     Chrome would not (the previous version threw ReferenceError on
 *     canvas.toDataURL and WebGL getParameter).
 *  2. every override reports itself as a native function via a patched
 *     Function.prototype.toString (anti anti-debug "native code" check).
 *  3. values are stable: same question, same answer, forever. No per-read
 *     randomness (fingerprint instability is itself a bot signal).
 *  4. never delete APIs that a real Chrome always has (WebRTC, fonts,
 *     AudioContext, Notification...). Removing them was a strong tell.
 *  5. spoof only what the identity defines; everything else stays real.
 */
(() => {
  'use strict';

  const I = (typeof __IDENTITY__ !== 'undefined') ? __IDENTITY__ : null;
  if (!I || !I.navigator) { return; }

  // ------------------------------------------------------------- infrastructure
  // One global Function.prototype.toString patch: any function we register
  // reports a native-looking source, including toString itself.
  const _origToString = Function.prototype.toString;
  const _nativeSource = new WeakMap();
  const _patchedToString = function toString() {
    const src = _nativeSource.get(this);
    return (src !== undefined) ? src : _origToString.call(this);
  };
  _nativeSource.set(_patchedToString, 'function toString() { [native code] }');
  try { Function.prototype.toString = _patchedToString; } catch (e) {}

  function registerNative(fn, name) {
    try { _nativeSource.set(fn, 'function ' + name + '() { [native code] }'); } catch (e) {}
    return fn;
  }

  // Replace a prototype method with a wrapper that can always fall back.
  function patchMethod(obj, name, wrapper) {
    try {
      const original = obj[name];
      if (typeof original !== 'function') { return; }
      const wrapped = function (...args) {
        try {
          return wrapper(this, original, args);
        } catch (e) {
          return original.apply(this, args);
        }
      };
      registerNative(wrapped, name);
      // WebIDL prototype operations are writable/configurable/enumerable
      Object.defineProperty(obj, name, {
        value: wrapped, writable: true, configurable: true, enumerable: true,
      });
    } catch (e) {}
  }

  // Replace a prototype getter, keeping the descriptor shape Chrome uses.
  function patchGetter(obj, name, getValue) {
    try {
      const getter = function () { return getValue(); };
      registerNative(getter, 'get ' + name);
      Object.defineProperty(obj, name, {
        get: getter, set: undefined, configurable: true, enumerable: true,
      });
    } catch (e) {}
  }

  function safe(fn) { try { fn(); } catch (e) {} }

  // ------------------------------------------------------- chromedriver residue
  // cdc_ variable names change across chromedriver builds: match the pattern,
  // not one hardcoded historical name.
  safe(() => {
    const cdcRe = /^\$?cdc_/i;
    for (const holder of [window, document]) {
      try {
        for (const key of Object.getOwnPropertyNames(holder)) {
          if (cdcRe.test(key)) {
            try { delete holder[key]; } catch (e) {}
          }
        }
      } catch (e) {}
    }
  });

  // ------------------------------------------------------------------ navigator
  // NOTE: platform, hardwareConcurrency and deviceMemory are deliberately
  // NOT spoofed. Web Workers expose the real values (script injection does
  // not reach worker contexts), so any main-thread claim that differs from
  // the host is an instant "inconsistent navigator" bot flag. The persona is
  // instead chosen to match the host OS (see browser_identity.host_os), so
  // the real values are already consistent everywhere.
  safe(() => {
    const N = Object.getPrototypeOf(navigator); // Navigator.prototype
    // real value in a clean profile is false, not undefined
    patchGetter(N, 'webdriver', () => false);
    if (I.navigator.vendor) { patchGetter(N, 'vendor', () => I.navigator.vendor); }
    if (I.navigator.languages) { patchGetter(N, 'languages', () => I.navigator.languages); }
  });

  // ----------------------------------------------------- user-agent client hints
  // navigator.userAgentData must agree with the UA string and with the
  // HTTP sec-ch-ua-* headers (overridden via CDP on the Python side).
  safe(() => {
    const ua = I.navigator.userAgentData;
    // real Chrome exposes userAgentData on secure contexts only
    if (!ua || !window.isSecureContext) { return; }
    const impl = {
      [Symbol.toStringTag]: 'NavigatorUAData',
      brands: ua.brands,
      mobile: ua.mobile,
      platform: ua.platform,
      getHighEntropyValues: registerNative(function getHighEntropyValues(hints) {
        const all = ua.highEntropy || {};
        const out = {};
        try {
          for (const h of (hints || [])) { if (h in all) { out[h] = all[h]; } }
        } catch (e) {}
        return Promise.resolve(out);
      }, 'getHighEntropyValues'),
      toJSON: registerNative(function toJSON() {
        return { brands: ua.brands, mobile: ua.mobile, platform: ua.platform };
      }, 'toJSON'),
    };
    patchGetter(Object.getPrototypeOf(navigator), 'userAgentData', () => impl);
  });

  // --------------------------------------------------------- plugins/mimeTypes
  // NOT spoofed. A real modern Chrome (headed and --headless=new since
  // ~Chrome 90) already exposes a genuine PluginArray with the 5 PDF
  // entries, which passes every structural check (instanceof PluginArray,
  // [object PluginArray] toString tag, Plugin items...). Our old fake was a
  // plain object and FAILED those checks - it replaced something correct
  // with something detectable. Faking plugins only ever mattered for the
  // long-dead classic headless, which reported zero plugins.

  // --------------------------------------------------------------------- screen
  // Patch individual properties on Screen.prototype so unknown/future
  // properties (orientation, isExtended, scale) stay real instead of
  // vanishing under a whole-object replacement.
  safe(() => {
    if (typeof Screen === 'undefined' || !I.screen) { return; }
    const props = {
      width: I.screen.width,
      height: I.screen.height,
      availWidth: I.screen.avail_width,
      availHeight: I.screen.avail_height,
      availLeft: I.screen.avail_left,
      availTop: I.screen.avail_top,
      colorDepth: 24,
      pixelDepth: 24,
    };
    for (const key of Object.keys(props)) {
      patchGetter(Screen.prototype, key, () => props[key]);
    }
  });

  // --------------------------------------------------------------------- canvas
  // Deterministic, identity-seeded noise: same canvas -> same output on every
  // call and every page (stable), different from any other identity.
  safe(() => {
    if (typeof HTMLCanvasElement === 'undefined') { return; }

    function hash32(a, b, c) {
      let h = (a ^ 0x9e3779b9) >>> 0;
      h = Math.imul(h ^ b, 0x85ebca6b) >>> 0;
      h = Math.imul(h ^ c, 0xc2b2ae35) >>> 0;
      h ^= h >>> 16;
      return h >>> 0;
    }
    function mulberry32(seed) {
      let t = seed >>> 0;
      return function () {
        t = (t + 0x6d2b79f5) >>> 0;
        let r = Math.imul(t ^ (t >>> 15), 1 | t);
        r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
        return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
      };
    }
    function paintNoise(canvas) {
      try {
        if (!canvas.width || !canvas.height) { return; }
        const ctx = canvas.getContext('2d');
        if (!ctx) { return; }
        const rnd = mulberry32(hash32(I.seed || 1, canvas.width, canvas.height));
        ctx.fillStyle = 'rgba(8,8,8,0.02)';
        for (let i = 0; i < 16; i++) {
          ctx.fillRect(
            Math.floor(rnd() * canvas.width),
            Math.floor(rnd() * canvas.height),
            1, 1
          );
        }
      } catch (e) {}
    }

    patchMethod(HTMLCanvasElement.prototype, 'toDataURL', (self, orig, args) => {
      paintNoise(self);
      return orig.apply(self, args);
    });
    if (typeof HTMLCanvasElement.prototype.toBlob === 'function') {
      patchMethod(HTMLCanvasElement.prototype, 'toBlob', (self, orig, args) => {
        paintNoise(self);
        return orig.apply(self, args);
      });
    }
    if (typeof CanvasRenderingContext2D !== 'undefined') {
      patchMethod(CanvasRenderingContext2D.prototype, 'getImageData', (self, orig, args) => {
        const out = orig.apply(self, args);
        try {
          const x = args[0] | 0, y = args[1] | 0, w = args[2] | 0;
          const rnd = mulberry32(hash32(I.seed || 1, x + 31, y + 7, w));
          const d = out.data;
          for (let i = 0; i < 8 && d.length >= 4; i++) {
            const idx = (Math.floor(rnd() * (d.length >> 2))) << 2;
            d[idx] = (d[idx] + 1) & 0xff; // deterministic +/-1 on one channel
          }
        } catch (e) { /* return untouched data */ }
        return out;
      });
    }
  });

  // ---------------------------------------------------------------------- WebGL
  // Only six enums are identity-relevant; everything else delegates to the
  // real implementation (the old version broke every other query).
  safe(() => {
    const ENUMS = {
      37445: 'unmasked_vendor',  // UNMASKED_VENDOR_WEBGL
      37446: 'unmasked_renderer', // UNMASKED_RENDERER_WEBGL
      7936: 'vendor',            // VENDOR
      7937: 'renderer',          // RENDERER
      7938: 'version',           // VERSION
      35724: 'shading_language_version', // SHADING_LANGUAGE_VERSION
    };
    function patch(proto) {
      if (!proto || typeof proto.getParameter !== 'function') { return; }
      patchMethod(proto, 'getParameter', (self, orig, args) => {
        const key = ENUMS[args[0]];
        if (key && I.webgl && I.webgl[key]) { return I.webgl[key]; }
        return orig.apply(self, args);
      });
    }
    patch(typeof WebGLRenderingContext !== 'undefined' ? WebGLRenderingContext.prototype : null);
    patch(typeof WebGL2RenderingContext !== 'undefined' ? WebGL2RenderingContext.prototype : null);
  });

  // Intentionally NOT spoofed (each of these was a detection vector before):
  //   RTCPeerConnection, Notification, document.fonts, AudioContext,
  //   performance.memory - a real Chrome always has them; deleting or
  //   half-faking them is a stronger signal than whatever they leak.
})();
