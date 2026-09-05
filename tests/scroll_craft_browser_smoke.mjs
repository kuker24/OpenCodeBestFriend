#!/usr/bin/env node

import { createServer } from "node:http";
import { mkdtemp, readFile, rm, stat } from "node:fs/promises";
import { homedir, tmpdir } from "node:os";
import { dirname, extname, join, resolve, sep } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const HELPER = join(ROOT, "bin", "opencode-chromium-cdp");
const FIXTURE_URL_PATH = "/tests/fixtures/scroll-craft/";

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

class CdpClient {
  constructor(url) {
    this.url = url;
    this.id = 0;
    this.pending = new Map();
    this.handlers = new Map();
  }

  async open() {
    this.ws = new WebSocket(this.url);
    this.ws.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (message.id) {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(message.error.message));
        else pending.resolve(message.result);
        return;
      }
      for (const handler of this.handlers.get(message.method) || []) handler(message.params || {});
    });
    await new Promise((resolveOpen, rejectOpen) => {
      this.ws.addEventListener("open", resolveOpen, { once: true });
      this.ws.addEventListener("error", rejectOpen, { once: true });
    });
  }

  on(method, handler) {
    const handlers = this.handlers.get(method) || [];
    handlers.push(handler);
    this.handlers.set(method, handlers);
  }

  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolveSend, rejectSend) => {
      this.pending.set(id, { resolve: resolveSend, reject: rejectSend });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(source) {
    const result = await this.send("Runtime.evaluate", {
      expression: `(async () => { ${source} })()`,
      awaitPromise: true,
      returnByValue: true,
    });
    if (result.exceptionDetails) {
      const detail = result.exceptionDetails.exception?.description || result.exceptionDetails.text;
      throw new Error(`Browser evaluation failed: ${detail}`);
    }
    return result.result.value;
  }

  close() {
    this.ws?.close();
  }
}

async function startFixtureServer() {
  const server = createServer(async (request, response) => {
    const pathname = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
    if (pathname === "/__slow.mp4") {
      const timer = setTimeout(() => {
        response.writeHead(200, { "content-type": "video/mp4" });
        response.end("delayed");
      }, 10_000);
      request.on("close", () => clearTimeout(timer));
      return;
    }
    if (pathname === "/__clip.mp4") {
      response.writeHead(200, { "content-type": "video/mp4", "cache-control": "no-store" });
      response.end("scrollcraft-lifecycle-probe");
      return;
    }
    if (pathname === "/favicon.ico") {
      response.writeHead(204);
      response.end();
      return;
    }

    try {
      let file = resolve(ROOT, `.${pathname}`);
      assert(file === ROOT || file.startsWith(`${ROOT}${sep}`), "Static path escaped repository root");
      if ((await stat(file)).isDirectory()) file = join(file, "index.html");
      const body = await readFile(file);
      const types = {
        ".css": "text/css; charset=utf-8",
        ".html": "text/html; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".svg": "image/svg+xml",
      };
      response.writeHead(200, {
        "content-type": types[extname(file)] || "application/octet-stream",
        "cache-control": "no-store",
      });
      response.end(body);
    } catch {
      response.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
      response.end("not found");
    }
  });
  await new Promise((resolveListen) => server.listen(0, "127.0.0.1", resolveListen));
  return { server, port: server.address().port };
}

const AUDIT_SCRIPT = `
(() => {
  if (window.__scAudit) return;
  const listeners = [];
  const nativeAdd = EventTarget.prototype.addEventListener;
  const nativeRemove = EventTarget.prototype.removeEventListener;
  const capture = (options) => typeof options === 'boolean' ? options : Boolean(options && options.capture);
  EventTarget.prototype.addEventListener = function(type, handler, options) {
    const cap = capture(options);
    if (handler && !listeners.some((x) => x.target === this && x.type === type && x.handler === handler && x.capture === cap)) {
      listeners.push({ target: this, type, handler, capture: cap });
    }
    return nativeAdd.call(this, type, handler, options);
  };
  EventTarget.prototype.removeEventListener = function(type, handler, options) {
    const cap = capture(options);
    const index = listeners.findIndex((x) => x.target === this && x.type === type && x.handler === handler && x.capture === cap);
    if (index > -1) listeners.splice(index, 1);
    return nativeRemove.call(this, type, handler, options);
  };

  const rafs = new Set();
  const nativeRaf = window.requestAnimationFrame.bind(window);
  const nativeCancelRaf = window.cancelAnimationFrame.bind(window);
  window.requestAnimationFrame = function(handler) {
    let id = 0;
    id = nativeRaf((now) => { rafs.delete(id); handler(now); });
    rafs.add(id);
    return id;
  };
  window.cancelAnimationFrame = function(id) { rafs.delete(id); return nativeCancelRaf(id); };

  const timers = new Set();
  const nativeTimeout = window.setTimeout.bind(window);
  const nativeClearTimeout = window.clearTimeout.bind(window);
  window.setTimeout = function(handler, delay, ...args) {
    let id = 0;
    id = nativeTimeout(() => { timers.delete(id); handler(...args); }, delay);
    timers.add(id);
    return id;
  };
  window.clearTimeout = function(id) { timers.delete(id); return nativeClearTimeout(id); };

  const observers = new Set();
  const NativeIntersectionObserver = window.IntersectionObserver;
  if (NativeIntersectionObserver) {
    window.IntersectionObserver = function(handler, options) {
      const observer = new NativeIntersectionObserver(handler, options);
      const nativeDisconnect = observer.disconnect.bind(observer);
      observer.disconnect = function() { observers.delete(observer); return nativeDisconnect(); };
      observers.add(observer);
      return observer;
    };
    window.IntersectionObserver.prototype = NativeIntersectionObserver.prototype;
  }

  const objectUrls = [];
  const revokedUrls = [];
  const nativeCreateUrl = URL.createObjectURL.bind(URL);
  const nativeRevokeUrl = URL.revokeObjectURL.bind(URL);
  URL.createObjectURL = function(blob) { const url = nativeCreateUrl(blob); objectUrls.push(url); return url; };
  URL.revokeObjectURL = function(url) { revokedUrls.push(url); return nativeRevokeUrl(url); };

  const fetchSignals = [];
  const nativeFetch = window.fetch.bind(window);
  window.fetch = function(input, options) {
    if (String(input).includes('__slow.mp4')) fetchSignals.push(options && options.signal);
    return nativeFetch(input, options);
  };

  window.__scAudit = {
    fetchSignals,
    snapshot() {
      return {
        listeners: listeners.length,
        observers: observers.size,
        rafs: rafs.size,
        timers: timers.size,
        objectUrls: objectUrls.slice(),
        revokedUrls: revokedUrls.slice(),
      };
    },
  };
})();`;

async function waitFor(client, source, message, attempts = 80) {
  for (let i = 0; i < attempts; i += 1) {
    if (await client.evaluate(`return Boolean(${source});`)) return;
    await delay(50);
  }
  throw new Error(message);
}

async function navigate(client, url) {
  await client.send("Page.navigate", { url });
  await waitFor(
    client,
    "document.readyState === 'complete' && Boolean(window.__scrollCraftFixture)",
    `Fixture did not become ready: ${url}`,
  );
}

async function settle(client) {
  await client.evaluate(`
    await new Promise((resolveFrame) => requestAnimationFrame(() => requestAnimationFrame(resolveFrame)));
    return true;
  `);
}

async function sampleAct(client, selector, expected) {
  return client.evaluate(`
    const el = document.querySelector(${JSON.stringify(selector)});
    const rect = el.getBoundingClientRect();
    const top = rect.top + scrollY;
    const pinned = el.classList.contains('sc-act--pinned');
    const target = pinned
      ? top + Math.max(rect.height - innerHeight, 1) * ${expected}
      : top - innerHeight + (rect.height + innerHeight) * ${expected};
    scrollTo(0, target);
    await new Promise((resolveFrame) => requestAnimationFrame(() => requestAnimationFrame(resolveFrame)));
    const stage = el.querySelector('[data-sc-stage]');
    const cue = el.querySelector('[data-sc-cue]');
    return {
      progress: parseFloat(getComputedStyle(el).getPropertyValue('--sc-p')),
      cueOpacity: cue ? parseFloat(getComputedStyle(cue).opacity) : null,
      stagePosition: stage ? getComputedStyle(stage).position : null,
      stageHeight: stage ? stage.getBoundingClientRect().height : null,
      railX: el.querySelector('[data-sc-pan]')
        ? new DOMMatrix(getComputedStyle(el.querySelector('[data-sc-pan]')).transform).m41
        : null,
    };
  `);
}

function assertSameResources(actual, expected, label) {
  for (const key of ["listeners", "observers", "rafs", "timers"]) {
    assert(actual[key] === expected[key], `${label}: ${key} leaked (${expected[key]} -> ${actual[key]})`);
  }
}

async function main() {
  const temp = await mkdtemp(join(tmpdir(), "ocbf-scroll-craft-"));
  const resolved = spawnSync(HELPER, ["resolve"], { encoding: "utf8", env: process.env });
  assert(resolved.status === 0, resolved.stderr || "Chromium is NOT_CONFIGURED");
  const chromium = process.env.OPENCODE_CHROMIUM_BIN || resolved.stdout.trim();
  const profile = chromium.includes("/snap/")
    ? join(homedir(), "snap", "chromium", "common", `ocbf-scroll-craft-${process.pid}`)
    : join(temp, "profile");
  const cdpPort = 13000 + (process.pid % 10000);
  const browserEnv = {
    ...process.env,
    OPENCODE_CHROMIUM_BIN: chromium,
    OPENCODE_CHROMIUM_CDP_PORT: String(cdpPort),
    OPENCODE_CHROMIUM_STATE: join(temp, "state"),
    OPENCODE_CHROMIUM_PROFILE: profile,
  };
  const start = spawnSync(HELPER, ["start"], { encoding: "utf8", env: browserEnv });
  assert(start.status === 0, start.stderr || start.stdout || "Chromium failed to start");

  let fixture;
  let client;
  try {
    fixture = await startFixtureServer();
    const baseUrl = `http://127.0.0.1:${fixture.port}${FIXTURE_URL_PATH}`;
    const targets = await fetch(`http://127.0.0.1:${cdpPort}/json/list`).then((response) => response.json());
    const target = targets.find((item) => item.type === "page");
    assert(target?.webSocketDebuggerUrl, "No Chromium page target exposed over CDP");
    client = new CdpClient(target.webSocketDebuggerUrl);
    await client.open();

    const errors = [];
    const requests = [];
    client.on("Runtime.exceptionThrown", (params) => errors.push(params.exceptionDetails?.text || "exception"));
    client.on("Runtime.consoleAPICalled", (params) => {
      if (params.type === "error") errors.push(params.args?.map((arg) => arg.value || arg.description).join(" ") || "console.error");
    });
    client.on("Log.entryAdded", (params) => {
      if (params.entry?.level === "error") errors.push(params.entry.text);
    });
    client.on("Network.requestWillBeSent", (params) => requests.push(params.request.url));
    await Promise.all([
      client.send("Page.enable"),
      client.send("Runtime.enable"),
      client.send("Log.enable"),
      client.send("Network.enable"),
    ]);
    await client.send("Page.addScriptToEvaluateOnNewDocument", { source: AUDIT_SCRIPT });
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1440,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await client.send("Emulation.setEmulatedMedia", {
      media: "screen",
      features: [{ name: "prefers-reduced-motion", value: "no-preference" }],
    });
    await navigate(client, `${baseUrl}?desktop=1`);

    const initial = await client.evaluate(`return {
      acts: document.querySelectorAll('[data-sc-act]').length,
      instances: ScrollCraft.instances.length,
      viewport: [innerWidth, innerHeight],
      width: document.documentElement.scrollWidth,
    };`);
    assert(initial.acts === 5, `Expected 5 acts, found ${initial.acts}`);
    assert(initial.instances === 1, `Expected one mounted instance, found ${initial.instances}`);
    assert(initial.viewport[0] === 1440 && initial.viewport[1] === 900, `Unexpected desktop viewport ${initial.viewport}`);
    assert(initial.width <= initial.viewport[0] + 1, `Desktop horizontal overflow: ${initial.width}px`);

    const selectors = ["#open", "#proof", ".evidence", "#range", "#cta"];
    const positions = [0, 0.2, 0.4, 0.6, 0.8, 1];
    const samples = {};
    for (const selector of selectors) {
      samples[selector] = [];
      for (const position of positions) {
        const sample = await sampleAct(client, selector, position);
        assert(Number.isFinite(sample.progress), `${selector} did not publish finite progress`);
        assert(Math.abs(sample.progress - position) <= 0.035, `${selector} progress ${sample.progress} missed ${position}`);
        samples[selector].push(sample);
      }
    }
    for (const selector of ["#open", "#proof", "#cta"]) {
      const peak = Math.max(...samples[selector].map((sample) => sample.cueOpacity));
      assert(peak >= 0.95, `${selector} cue never became fully legible (${peak})`);
      const middle = samples[selector][2];
      assert(middle.stagePosition === "sticky", `${selector} stage is not sticky`);
      assert(middle.stageHeight >= 850, `${selector} stage is blank or collapsed`);
    }
    const panStart = samples["#range"][1].railX;
    const panEnd = samples["#range"][4].railX;
    assert(Math.abs(panEnd - panStart) > 100, `Pan rail did not travel (${panStart} -> ${panEnd})`);
    const reverseHigh = await sampleAct(client, "#range", 0.75);
    const reverseLow = await sampleAct(client, "#range", 0.25);
    assert(reverseLow.progress < reverseHigh.progress, "Reverse scroll did not lower act progress");
    assert(reverseLow.railX > reverseHigh.railX, "Reverse scroll did not reverse the pan rail");

    await client.evaluate(`document.querySelector('.skip').focus(); return document.activeElement.className;`);
    await client.send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
    await client.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
    await waitFor(client, "location.hash === '#cta'", "Keyboard skip link did not reach #cta");
    await settle(client);
    const anchor = await client.evaluate(`
      const cue = document.querySelector('#cta [data-sc-cue]');
      return { progress: parseFloat(getComputedStyle(document.querySelector('#cta')).getPropertyValue('--sc-p')), opacity: parseFloat(getComputedStyle(cue).opacity) };
    `);
    assert(anchor.progress > 0.2 && anchor.progress < 0.9, `Anchor landed at unreadable progress ${anchor.progress}`);
    assert(anchor.opacity > 0.85, `Anchor CTA remained hidden at opacity ${anchor.opacity}`);

    await client.evaluate(`document.querySelector('#cta a').focus(); return true;`);
    await settle(client);
    const focused = await client.evaluate(`return {
      focused: document.activeElement === document.querySelector('#cta a'),
      opacity: parseFloat(getComputedStyle(document.querySelector('#cta [data-sc-cue]')).opacity),
    };`);
    assert(focused.focused && focused.opacity > 0.85, "Focused CTA was not visible and keyboard-reachable");
    assert(errors.length === 0, `Desktop fixture emitted errors: ${errors.join(" | ")}`);

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 390,
      height: 844,
      deviceScaleFactor: 2,
      mobile: true,
      screenWidth: 390,
      screenHeight: 844,
    });
    await navigate(client, `${baseUrl}?mobile=1`);
    const mobile = await client.evaluate(`return {
      viewport: [innerWidth, innerHeight],
      width: document.documentElement.scrollWidth,
      acts: document.querySelectorAll('[data-sc-act]').length,
    };`);
    assert(mobile.viewport[0] === 390 && mobile.viewport[1] === 844, `Unexpected mobile viewport ${mobile.viewport}`);
    assert(mobile.width <= mobile.viewport[0] + 1, `Mobile horizontal overflow: ${mobile.width}px`);
    assert(mobile.acts === 5, "Mobile fixture lost acts");
    const mobileRange = await sampleAct(client, "#range", 0.5);
    assert(Math.abs(mobileRange.progress - 0.5) <= 0.035, `Mobile pan progress was ${mobileRange.progress}`);

    await client.send("Emulation.setEmulatedMedia", {
      media: "screen",
      features: [{ name: "prefers-reduced-motion", value: "reduce" }],
    });
    await navigate(client, `${baseUrl}?reduced=1`);
    await sampleAct(client, "#range", 0.5);
    const reduced = await client.evaluate(`return {
      active: ScrollCraft.reduce,
      parallax: getComputedStyle(document.querySelector('[data-sc-parallax]')).transform,
      rail: getComputedStyle(document.querySelector('[data-sc-pan]')).transform,
      cue: parseFloat(getComputedStyle(document.querySelector('#open [data-sc-cue]')).opacity),
      railFits: document.querySelector('[data-sc-pan]').scrollWidth <= document.querySelector('[data-sc-stage]').clientWidth + 1,
    };`);
    assert(reduced.active, "Reduced-motion media query was not honored");
    assert(reduced.parallax === "none" && reduced.rail === "none", "Reduced motion retained positional transforms");
    assert(reduced.cue >= 0.99, `Reduced-motion copy was hidden at opacity ${reduced.cue}`);
    assert(reduced.railFits, "Reduced-motion rail content was not reachable");
    assert(errors.length === 0, `Fixture emitted browser errors: ${errors.join(" | ")}`);

    await client.send("Emulation.setEmulatedMedia", {
      media: "screen",
      features: [{ name: "prefers-reduced-motion", value: "no-preference" }],
    });
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1440,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await navigate(client, `${baseUrl}?lifecycle=1`);
    await client.evaluate(`window.__scrollCraftFixture.destroy(); return true;`);
    await delay(100);
    const staticFallback = await client.evaluate(`return {
      ready: document.documentElement.classList.contains('sc-ready'),
      pinned: document.querySelector('#open').classList.contains('sc-act--pinned'),
      height: document.querySelector('#open').style.height,
      cueOpacity: parseFloat(getComputedStyle(document.querySelector('#open [data-sc-cue]')).opacity),
    };`);
    assert(!staticFallback.ready, "destroy() left the document marked ready");
    assert(!staticFallback.pinned && staticFallback.height === "", "destroy() left pinned layout mutations behind");
    assert(staticFallback.cueOpacity >= 0.99, "destroy() did not restore readable static content");
    const clean = await client.evaluate(`return __scAudit.snapshot();`);
    const cycled = await client.evaluate(`
      const cycle = ScrollCraft.mount(document);
      await new Promise((resolveFrame) => requestAnimationFrame(() => requestAnimationFrame(resolveFrame)));
      cycle.destroy();
      return true;
    `);
    assert(cycled, "Lifecycle remount did not run");
    await delay(100);
    assertSameResources(await client.evaluate(`return __scAudit.snapshot();`), clean, "document remount");

    await client.evaluate(`
      const root = document.createElement('div');
      root.id = 'slow-lifecycle-root';
      root.innerHTML = '<section data-sc-act="scrub" data-sc-span="1.5"><div data-sc-stage><video data-sc-scrub data-sc-src="/__slow.mp4"></video></div></section>';
      document.querySelector('main').prepend(root);
      scrollTo(0, 0);
      window.__slowLifecycle = { root, instance: ScrollCraft.mount(root) };
      return true;
    `);
    await waitFor(client, "__scAudit.fetchSignals.length > 0", "Clip fetch did not expose an AbortSignal");
    await client.evaluate(`__slowLifecycle.instance.destroy(); __slowLifecycle.root.remove(); return true;`);
    const aborted = await client.evaluate(`return __scAudit.fetchSignals.every((signal) => signal && signal.aborted);`);
    assert(aborted, "destroy() did not abort the pending clip fetch");
    await delay(100);
    assertSameResources(await client.evaluate(`return __scAudit.snapshot();`), clean, "fetch abort");

    const beforeUrls = await client.evaluate(`return __scAudit.snapshot().objectUrls.length;`);
    await client.evaluate(`
      const root = document.createElement('div');
      root.id = 'blob-lifecycle-root';
      root.innerHTML = '<section data-sc-act="scrub" data-sc-span="1.5"><div data-sc-stage><video data-sc-scrub data-sc-src="/__clip.mp4"></video></div></section>';
      document.querySelector('main').prepend(root);
      scrollTo(0, 0);
      window.__blobLifecycle = { root, instance: ScrollCraft.mount(root) };
      return true;
    `);
    await waitFor(client, `__scAudit.snapshot().objectUrls.length > ${beforeUrls}`, "Clip fetch did not create a Blob URL");
    const createdUrl = await client.evaluate(`return __scAudit.snapshot().objectUrls.at(-1);`);
    await client.evaluate(`__blobLifecycle.instance.destroy(); __blobLifecycle.root.remove(); return true;`);
    await delay(100);
    const afterBlob = await client.evaluate(`return __scAudit.snapshot();`);
    assert(afterBlob.revokedUrls.includes(createdUrl), "destroy() did not revoke the clip Blob URL");
    assertSameResources(afterBlob, clean, "Blob URL cleanup");
    const instances = await client.evaluate(`return ScrollCraft.instances.length;`);
    assert(instances === 0, `Destroyed instances remained registered: ${instances}`);

    const external = requests.filter((url) => {
      if (/^(about:|data:|blob:)/.test(url)) return false;
      try {
        const parsed = new URL(url);
        return parsed.hostname !== "127.0.0.1" || Number(parsed.port) !== fixture.port;
      } catch {
        return true;
      }
    });
    assert(external.length === 0, `Fixture made external requests: ${external.join(", ")}`);

    console.log(JSON.stringify({
      status: "PASS",
      desktop: initial.viewport,
      mobile: mobile.viewport,
      sampledActs: selectors.length,
      samplesPerAct: positions.length,
      reverse: true,
      keyboardAndAnchor: true,
      reducedMotion: true,
      lifecycle: { abort: true, revoke: true, remount: true },
      externalRequests: external.length,
      browserErrors: errors.length,
    }, null, 2));
  } finally {
    client?.close();
    if (fixture) await new Promise((resolveClose) => fixture.server.close(resolveClose));
    spawnSync(HELPER, ["stop"], { encoding: "utf8", env: browserEnv });
    await rm(temp, { recursive: true, force: true });
    if (profile.includes(`ocbf-scroll-craft-${process.pid}`)) await rm(profile, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
