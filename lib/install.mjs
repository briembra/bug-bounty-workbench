/**
 * Copy the method into an agent's directories, and take it back out again.
 *
 * Nothing here is clever: it reads files from the package, optionally trims
 * frontmatter keys the target agent does not define, and writes them to a
 * known directory. A manifest records exactly what was written, per agent and
 * scope, so uninstall removes those files and nothing else.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { AGENTS, BUNDLE, DROP_KEYS, SKILL_NAME } from './agents.mjs';

const MANIFEST = '.bbw-manifest.json';
const FRONT = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/;
const HERE = path.dirname(fileURLToPath(import.meta.url));

export function trimFrontmatter(text) {
  const match = FRONT.exec(text);
  if (!match) return text;
  const kept = match[1]
    .split(/\r?\n/)
    .filter((line) => !DROP_KEYS.includes(line.split(':')[0].trim()));
  return `---\n${kept.join('\n')}\n---\n${text.slice(match[0].length)}`;
}

export function commandFiles(root) {
  const dir = path.join(root, 'commands');
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((name) => name.endsWith('.md') && name !== 'README.md')
    .sort();
}

/**
 * Build the list of { from, to } copies for one agent.
 *
 * `scope` is 'project' or 'global'. A null `commands` or `skill` path means the
 * agent has no such directory and that part is skipped.
 */
export function planInstall({ agent, scope, root, cwd, home }) {
  const spec = AGENTS[agent];
  if (!spec) throw new Error(`unknown agent: ${agent}`);

  const targets = scope === 'global' ? spec.global : spec.project;
  if (!targets) throw new Error(`${agent} has no ${scope} install path`);

  const copies = [];

  if (targets.commands) {
    const dir = path.isAbsolute(targets.commands)
      ? targets.commands
      : path.join(cwd, targets.commands);
    for (const name of commandFiles(root)) {
      copies.push({
        from: path.join(root, 'commands', name),
        to: path.join(dir, `bbw-${name}`),
        transform: agent !== 'claude',
      });
    }
  }

  if (targets.skill) {
    const dir = path.isAbsolute(targets.skill) ? targets.skill : path.join(cwd, targets.skill);
    for (const entry of BUNDLE) {
      const source = path.join(root, entry);
      if (!fs.existsSync(source)) continue;
      if (fs.statSync(source).isDirectory()) {
        for (const name of fs.readdirSync(source)) {
          if (name === '__pycache__') continue;
          const child = path.join(source, name);
          if (!fs.statSync(child).isFile()) continue;
          copies.push({
            from: child,
            to: path.join(dir, entry, name),
            transform: agent !== 'claude',
          });
        }
      } else {
        copies.push({
          from: source,
          to: path.join(dir, entry),
          transform: entry.endsWith('.md') && agent !== 'claude',
        });
      }
    }
  }

  const manifestDir = scope === 'global' ? home : cwd;
  return {
    agent,
    scope,
    copies,
    manifest: path.join(manifestDir, MANIFEST),
    commandsDir: targets.commands,
    skillDir: targets.skill,
  };
}

export function version() {
  try {
    return JSON.parse(fs.readFileSync(path.join(HERE, '..', 'package.json'), 'utf8')).version;
  } catch {
    return '0.0.0';
  }
}

export function emptyManifest() {
  return { name: SKILL_NAME, version: version(), installs: [] };
}

export function applyInstall(plan, { dryRun = false } = {}) {
  const written = [];
  for (const copy of plan.copies) {
    if (!dryRun) {
      fs.mkdirSync(path.dirname(copy.to), { recursive: true });
      const data = copy.transform
        ? trimFrontmatter(fs.readFileSync(copy.from, 'utf8'))
        : fs.readFileSync(copy.from);
      fs.writeFileSync(copy.to, data);
    }
    written.push(copy.to);
  }

  if (dryRun) return { files: written, dryRun: true };

  const record = readManifest(plan.manifest) ?? emptyManifest();
  const previous = record.installs.find(
    (entry) => entry.agent === plan.agent && entry.scope === plan.scope,
  );

  // A rename between versions leaves the old file behind unless it is named
  // here. Only files this installer recorded are ever removed.
  const stale = (previous?.files ?? []).filter((file) => !written.includes(file));
  const removed = [];
  for (const file of stale) {
    if (!fs.existsSync(file)) continue;
    fs.rmSync(file, { force: true });
    removed.push(file);
  }
  if (removed.length) prune(removed);

  record.version = version();
  record.installs = record.installs.filter(
    (entry) => !(entry.agent === plan.agent && entry.scope === plan.scope),
  );
  record.installs.push({
    agent: plan.agent,
    scope: plan.scope,
    version: version(),
    previousVersion: previous?.version ?? null,
    installedAt: new Date().toISOString(),
    files: written,
  });
  fs.writeFileSync(plan.manifest, `${JSON.stringify(record, null, 2)}\n`);
  return { files: written, removed, manifest: plan.manifest };
}

export function readManifest(file) {
  try {
    const parsed = JSON.parse(fs.readFileSync(file, 'utf8'));
    if (!Array.isArray(parsed.installs)) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function removeInstall(manifestFile, { dryRun = false, agent = null } = {}) {
  const record = readManifest(manifestFile);
  if (!record) return { removed: [], missing: true };

  const keep = [];
  const removed = [];
  for (const entry of record.installs) {
    if (agent && entry.agent !== agent) {
      keep.push(entry);
      continue;
    }
    for (const file of entry.files) {
      if (!fs.existsSync(file)) continue;
      if (!dryRun) fs.rmSync(file, { force: true });
      removed.push(file);
    }
  }

  if (!dryRun) {
    if (keep.length) {
      record.installs = keep;
      fs.writeFileSync(manifestFile, `${JSON.stringify(record, null, 2)}\n`);
    } else {
      fs.rmSync(manifestFile, { force: true });
    }
    prune(removed);
  }

  return { removed, kept: keep };
}

/** Remove directories the install created that are now empty, deepest first. */
function prune(files) {
  const dirs = Array.from(new Set(files.map((file) => path.dirname(file))))
    .sort((a, b) => b.length - a.length);
  for (const dir of dirs) {
    let current = dir;
    while (current && current !== path.dirname(current)) {
      try {
        if (fs.readdirSync(current).length === 0) fs.rmdirSync(current);
        else break;
      } catch {
        break;
      }
      current = path.dirname(current);
    }
  }
}

export function manifestAt(scope, { cwd, home }) {
  return path.join(scope === 'global' ? home : cwd, MANIFEST);
}

export { MANIFEST };
