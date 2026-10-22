import { groupBlocks, markSeen, takeNewBlocks } from "./blocks";

const b = (block, tool_type = "python") => ({ block, tool_type, feedback: "", success: true });

test("finds new blocks even when they are not at the end", () => {
  const seen = new Map();
  markSeen(seen, [b("c1"), b("c2"), b("f1", "file")]);
  // The coder ran again: its block lands before the file agent's old one.
  const fresh = takeNewBlocks(seen, [b("c1"), b("c2"), b("c3"), b("f1", "file")]);
  expect(fresh.map((x) => x.block)).toEqual(["c3"]);
  expect(takeNewBlocks(seen, [b("c1"), b("c2"), b("c3"), b("f1", "file")])).toEqual([]);
});

test("a command that really ran twice shows twice, a shrunk list shows nothing", () => {
  const seen = new Map();
  markSeen(seen, [b("ls")]);
  expect(takeNewBlocks(seen, [b("ls"), b("ls")]).map((x) => x.block)).toEqual(["ls"]);
  // The planner pointing at a sub-agent's shorter list is not news.
  expect(takeNewBlocks(seen, [b("ls")])).toEqual([]);
});

test("groupBlocks folds repeated commands and keeps every run", () => {
  const groups = groupBlocks([
    { tool_type: "bash", block: "ls", feedback: "a", success: true },
    { tool_type: "python", block: "x()", feedback: "", success: true },
    { tool_type: "bash", block: "ls", feedback: "b", success: false },
  ]);
  expect(groups.map((g) => [g.tool_type, g.block, g.runs.length])).toEqual([
    ["bash", "ls", 2],
    ["python", "x()", 1],
  ]);
  expect(groups[0].runs).toEqual([
    { feedback: "a", success: true },
    { feedback: "b", success: false },
  ]);
});
