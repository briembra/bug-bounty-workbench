/**
 * Where each agent expects commands and a skill, and how to recognise it.
 *
 * Project targets are relative to cwd. Global targets are absolute.
 * `bundle` is what gets copied into the skill directory: the router plus
 * everything it links to, so relative links still resolve after the copy.
 */

import { homedir } from 'node:os';
import { join } from 'node:path';

export const SKILL_NAME = 'bug-bounty-workbench';

export const BUNDLE = [
  'SKILL.md',
  'AGENTS.md',
  'PROMPT.md',
  'INSTALL.md',
  'README.md',
  'CONTRIBUTING.md',
  'DISCLAIMER.md',
  'LICENSE',
  'references',
  'workflows',
  'checklists',
  'templates',
  'prompts',
  'data',
  'commands',
];

const home = homedir();

export const AGENTS = {
  claude: {
    label: 'Claude Code',
    envKeys: ['CLAUDECODE', 'CLAUDE_CODE_ENTRYPOINT'],
    markerPaths: ['.claude'],
    project: {
      commands: '.claude/commands',
      skill: `.claude/skills/${SKILL_NAME}`,
    },
    global: {
      commands: join(home, '.claude', 'commands'),
      skill: join(home, '.claude', 'skills', SKILL_NAME),
    },
    hint: 'Restart Claude Code, then run /bbw-hunt',
  },

  opencode: {
    label: 'OpenCode',
    envKeys: ['OPENCODE', 'OPENCODE_CONFIG'],
    markerPaths: ['.opencode'],
    project: {
      commands: '.opencode/command',
      skill: `.opencode/skill/${SKILL_NAME}`,
    },
    global: {
      commands: join(home, '.config', 'opencode', 'command'),
      skill: join(home, '.config', 'opencode', 'skill', SKILL_NAME),
    },
    hint: 'Start a new session, then run /bbw-hunt',
  },

  cursor: {
    label: 'Cursor',
    envKeys: ['CURSOR_TRACE_ID', 'CURSOR_AGENT'],
    markerPaths: ['.cursor'],
    project: {
      commands: '.cursor/commands',
      skill: null,
    },
    global: {
      commands: join(home, '.cursor', 'commands'),
      skill: null,
    },
    hint: 'Reload the window, then type /bbw-hunt in chat',
  },

  codex: {
    label: 'Codex',
    envKeys: ['CODEX_HOME', 'CODEX_SANDBOX'],
    markerPaths: ['.codex'],
    project: {
      commands: null,
      skill: null,
    },
    global: {
      commands: join(home, '.codex', 'prompts'),
      skill: null,
    },
    hint: 'Run Codex from the repository, or pass the path in your first message',
  },
};

/** Frontmatter keys only Claude Code defines. Trimmed for everyone else. */
export const DROP_KEYS = ['allowed-tools', 'argument-hint'];

export function agentNames() {
  return Object.keys(AGENTS);
}

/**
 * Detect which agents are present.
 *
 * Project markers win over environment variables: a terminal opened inside
 * Claude Code often also has OPENCODE set when nested, and the directory the
 * user is standing in is the better signal. Returns names in a stable order.
 */
export function detectAgents({ cwd = process.cwd(), env = process.env, fs }) {
  const byEnv = [];
  const byDir = [];
  for (const [name, spec] of Object.entries(AGENTS)) {
    if (spec.envKeys.some((key) => env[key])) byEnv.push(name);
    const hasMarker = spec.markerPaths.some((relative) => {
      try {
        return fs.statSync(join(cwd, relative)).isDirectory();
      } catch {
        return false;
      }
    });
    if (hasMarker) byDir.push(name);
  }
  return byDir.length ? byDir : byEnv;
}
