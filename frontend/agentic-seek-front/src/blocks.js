/**
 * Which tool blocks are new since the last answer.
 *
 * /latest_answer returns every block of the session, joined agent by agent
 * (interaction.get_last_blocks_result), so new blocks are not always at the
 * end: a coder block can land before the file agent's older ones. Blocks are
 * therefore compared by content, with a count per content so a command that
 * really ran twice still shows twice.
 */

const keyOf = (block) => `${block.tool_type}\u0000${block.block}\u0000${block.feedback}`;

/** Remembers `blocks` as seen. `seen` is a Map of key -> count, updated in place. */
export function markSeen(seen, blocks) {
  takeNewBlocks(seen, blocks);
}

/** Returns the blocks not yet in `seen`, and adds them to it. */
export function takeNewBlocks(seen, blocks) {
  const counts = new Map();
  const fresh = [];
  for (const block of blocks) {
    const key = keyOf(block);
    const count = (counts.get(key) || 0) + 1;
    counts.set(key, count);
    if (count > (seen.get(key) || 0)) {
      fresh.push(block);
      seen.set(key, count);
    }
  }
  return fresh;
}

/**
 * Collapses runs of the same command (same tool and code) into one group,
 * in order of first appearance. Each group keeps every run's result.
 * Returns [{ tool_type, block, runs: [{ feedback, success }] }].
 */
export function groupBlocks(blocks) {
  const groups = [];
  const byCommand = new Map();
  for (const { tool_type, block, feedback, success } of blocks) {
    const key = `${tool_type}\u0000${block}`;
    let group = byCommand.get(key);
    if (!group) {
      group = { tool_type, block, runs: [] };
      byCommand.set(key, group);
      groups.push(group);
    }
    group.runs.push({ feedback, success });
  }
  return groups;
}
