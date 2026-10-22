// Fake AgenticSeek API for UI work: no models, no Python, no dependencies.
// Mirrors the response shapes of api.py and sources/files_api.py.
//   npm run mock                          (listens on :7777, token "dev")
//   PORT=8000 MOCK_TOKEN=secret npm run mock
// Queries containing "fail" return an error, "slow" take 15s, "browse" add a screenshot,
// "retry" runs the same command three times (two failures, then success).
const http = require("http");
const crypto = require("crypto");

const PORT = Number(process.env.PORT) || 7777;
const TOKEN = process.env.MOCK_TOKEN ?? "dev";

const files = new Map([
  ["notes.md", "# Notes\n\nThis workspace is fake, served by mock-backend.js."],
  ["src/main.py", 'def main():\n    print("hello from the agent")\n\nmain()\n'],
  ["src/utils.py", "def add(a, b):\n    return a + b\n"],
  ["logo.svg", '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><circle cx="32" cy="32" r="28" fill="#f97316"/></svg>'],
]);

const state = {
  generating: false,
  stopRequested: false,
  status: "Ready",
  agentName: "Jarvis",
  pending: null, // newest answer not yet served by /latest_answer
  history: [],
  blocks: {},
  screenshot: false,
};

const uid = () => crypto.randomUUID();
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const screenshotSvg = (query) => `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800">
  <rect width="100%" height="100%" fill="#f4f1ec"/>
  <rect x="40" y="40" width="1200" height="56" rx="28" fill="#fff" stroke="#ddd"/>
  <text x="80" y="76" font-family="monospace" font-size="20" fill="#555">https://search.example/?q=${encodeURIComponent(query).slice(0, 60)}</text>
  <rect x="40" y="140" width="760" height="24" rx="6" fill="#d6d3cd"/>
  <rect x="40" y="184" width="620" height="24" rx="6" fill="#e4e1db"/>
  <rect x="40" y="228" width="700" height="24" rx="6" fill="#e4e1db"/>
  <text x="40" y="760" font-family="monospace" font-size="18" fill="#999">mock screenshot ${new Date().toLocaleTimeString()}</text>
</svg>`;

// Agent names match api.py ("Jarvis" is config.ini's default agent_name).
const AGENTS = [
  [/code|python|script/i, "coder"],
  [/browse|search|web/i, "Browser"],
  [/file|workspace/i, "File Agent"],
  [/plan|trip/i, "Planner"],
];

const answerFor = (query) => ({
  agent: AGENTS.find(([test]) => test.test(query))?.[1] || "Jarvis",
  answer: `Here is a **mock** answer to:\n\n> ${query}\n\n- Lists render as markdown\n- So does \`inline code\`\n\n\`\`\`python\nprint("code blocks too")\n\`\`\``,
  reasoning: `The user asked "${query}". This reasoning text comes from mock-backend.js.`,
  blocks: /retry/i.test(query)
    ? [
        { block: "pip install requests", feedback: "ERROR: network unreachable", success: false, tool_type: "bash" },
        { block: "pip install requests", feedback: "ERROR: read timed out", success: false, tool_type: "bash" },
        { block: "pip install requests", feedback: "Successfully installed requests-2.32.3", success: true, tool_type: "bash" },
        { block: 'print("hello from the agent")', feedback: "hello from the agent", success: true, tool_type: "python" },
      ]
    : [
        { block: 'print("hello from the agent")', feedback: "hello from the agent", success: true, tool_type: "python" },
        { block: "ls missing_dir", feedback: "ls: missing_dir: No such file or directory", success: false, tool_type: "bash" },
      ],
});

const response = (fields) => ({
  done: "false",
  answer: "",
  reasoning: "",
  agent_name: state.agentName,
  success: "true",
  blocks: state.blocks,
  status: state.status,
  uid: uid(),
  ...fields,
});

async function runQuery(query) {
  const steps = ["Thinking...", "Planning steps", "Running tools", "Writing answer"];
  const stepMs = /slow/i.test(query) ? 3750 : 1000;
  for (const step of steps) {
    if (state.stopRequested) {
      state.pending = response({ done: "true", answer: "Stopped by user.", status: "Stopped" });
      return { code: 200, body: state.pending };
    }
    state.status = step;
    await sleep(stepMs);
  }
  if (/fail/i.test(query)) {
    return { code: 500, body: response({ answer: "An error occurred: mock failure", reasoning: "Error: mock failure", success: "false" }) };
  }
  const result = answerFor(query);
  state.agentName = result.agent;
  // Like interaction.get_last_blocks_result(): every block of the session, keyed "0", "1", ...
  const all = [...Object.values(state.blocks), ...result.blocks];
  state.blocks = Object.fromEntries(all.map((block, i) => [String(i), block]));
  if (/browse|search|web/i.test(query)) state.screenshot = query;
  const body = response({ done: "true", answer: result.answer, reasoning: result.reasoning, status: "Ready" });
  state.pending = body;
  return { code: 200, body };
}

// Minimal multipart parser: enough for the browser's FormData uploads.
function parseUploads(req, body) {
  const boundary = /boundary=(.+)$/.exec(req.headers["content-type"] || "")?.[1];
  if (!boundary) return [];
  return body
    .toString("latin1")
    .split(`--${boundary}`)
    .map((part) => /filename="([^"]+)"[\s\S]*?\r\n\r\n([\s\S]*)\r\n$/.exec(part))
    .filter(Boolean)
    .map(([, name, content]) => {
      const path = `uploads/${name}`;
      files.set(path, Buffer.from(content, "latin1").toString("utf8"));
      return path;
    });
}

function listDir(dir) {
  const prefix = dir ? `${dir}/` : "";
  const entries = new Map();
  for (const [path, content] of files) {
    if (!path.startsWith(prefix)) continue;
    const [name, ...rest] = path.slice(prefix.length).split("/");
    entries.set(name, {
      name,
      path: prefix + name,
      type: rest.length ? "directory" : "file",
      size: rest.length ? null : Buffer.byteLength(content),
    });
  }
  return [...entries.values()].sort(
    (a, b) => (a.type !== "directory") - (b.type !== "directory") || a.name.localeCompare(b.name)
  );
}

const routes = {
  "GET /health": () => ({ body: { status: "healthy", version: "0.1.0" } }),
  "GET /is_active": () => ({ body: { is_active: state.generating } }),
  "GET /stop": () => {
    state.stopRequested = state.generating;
    return { body: { status: "stopped" } };
  },
  "GET /latest_answer": () => {
    if (state.pending) {
      state.history.push(state.pending);
      state.pending = null;
    }
    const last = state.history[state.history.length - 1];
    if (!last && !state.generating) return { code: 404, body: { error: "No answer available" } };
    // While working, keep the last answer but report the live status, like the real agent.
    return { body: { ...(last || response({})), status: state.status } };
  },
  "POST /query": async (req, body) => {
    if (state.generating) return { code: 429, body: response({}) };
    const { query = "" } = JSON.parse(body.toString() || "{}");
    state.generating = true;
    state.stopRequested = false;
    try {
      return await runQuery(query);
    } finally {
      state.generating = false;
      state.status = "Ready";
    }
  },
  "GET /screenshot": () =>
    state.screenshot
      ? { type: "image/svg+xml", raw: screenshotSvg(state.screenshot) }
      : { code: 404, body: { error: "No screenshot available" } },
  "GET /files/list": (req, body, url) => {
    const path = url.searchParams.get("path") || "";
    if (path && !listDir(path).length) return { code: 404, body: { detail: "Directory not found" } };
    return { body: { path, entries: listDir(path) } };
  },
  "GET /files/content": (req, body, url) => {
    const path = url.searchParams.get("path");
    if (!files.has(path)) return { code: 404, body: { detail: "File not found" } };
    const content = files.get(path);
    const image = path.endsWith(".svg");
    return {
      body: {
        path,
        name: path.split("/").pop(),
        size: Buffer.byteLength(content),
        mime: image ? "image/svg+xml" : "text/plain",
        kind: image ? "image" : "text",
        content: image ? null : content,
        truncated: false,
      },
    };
  },
  "GET /files/raw": (req, body, url) => {
    const path = url.searchParams.get("path");
    if (!files.has(path) || !path.endsWith(".svg")) return { code: 415, body: { detail: "Only image files can be served raw" } };
    return { type: "image/svg+xml", raw: files.get(path) };
  },
  "POST /files/upload": (req, body) => ({ body: { paths: parseUploads(req, body) } }),
};

http
  .createServer(async (req, res) => {
    const origin = req.headers.origin;
    if (origin) {
      res.setHeader("Access-Control-Allow-Origin", origin);
      res.setHeader("Access-Control-Allow-Credentials", "true");
      res.setHeader("Access-Control-Allow-Headers", "Authorization, Content-Type");
      res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    }
    if (req.method === "OPTIONS") return res.writeHead(204).end();

    const url = new URL(req.url, "http://localhost");
    const route = routes[`${req.method} ${url.pathname}`];
    const send = ({ code = 200, body, type, raw }) => {
      res.writeHead(code, { "Content-Type": type || "application/json" });
      res.end(raw ?? JSON.stringify(body));
    };
    if (!route) return send({ code: 404, body: { detail: "Not Found" } });
    if (TOKEN && url.pathname !== "/health" && req.headers.authorization !== `Bearer ${TOKEN}`) {
      return send({ code: 401, body: { detail: "Missing or invalid API token" } });
    }
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    send(await route(req, Buffer.concat(chunks), url));
  })
  .listen(PORT, () => {
    console.log(`Mock AgenticSeek API on http://localhost:${PORT}`);
    console.log(TOKEN ? `API token: ${TOKEN}` : "Auth disabled (MOCK_TOKEN is empty)");
  });
