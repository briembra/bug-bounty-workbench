#!/usr/bin/env node
/**
 * bug-bounty-workbench — install the method into the agent you are running in.
 *
 *   npx bug-bounty-workbench setup
 *   npx bug-bounty-workbench setup --agent claude --global
 *   npx bug-bounty-workbench status
 *   npx bug-bounty-workbench uninstall
 */

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { AGENTS, agentNames, detectAgents } from '../lib/agents.mjs';
import { applyInstall, planInstall, readManifest, removeInstall } from '../lib/install.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const PKG = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));

const COLOR = process.stdout.isTTY && !process.env.NO_COLOR;
const paint = (code) => (text) => (COLOR ? `\u001b[${code}m${text}\u001b[0m` : text);
const bold = paint('1');
const dim = paint('2');
const green = paint('32');
const red = paint('31');

function parseArgs(argv) {
  const args = { _: [], agents: [], global: false, project: false, dryRun: false, json: false };
  for (const raw of argv) {
    if (raw === '--global' || raw === '-g') args.global = true;
    else if (raw === '--project' || raw === '-p') args.project = true;
    else if (raw === '--dry-run' || raw === '-n') args.dryRun = true;
    else if (raw === '--json') args.json = true;
    else if (raw === '--help' || raw === '-h') args.help = true;
    else if (raw === '--version' || raw === '-v') args.version = true;
    else if (raw.startsWith('--agent=')) args.agents.push(...raw.slice(8).split(','));
    else if (raw === '--agent') args.agents.push('__next__');
    else if (args.agents.at(-1) === '__next__') {
      args.agents[args.agents.length - 1] = raw;
      args.agents.push(...[]);
    } else args._.push(raw);
  }
  args.agents = args.agents.filter((name) => name && name !== '__next__');
  return args;
}

function help() {
  console.log(`${bold(`bug-bounty-workbench ${PKG.version}`)}
Authorized bug bounty hunting, installed into your agent.

Usage
  npx bug-bounty-workbench setup [options]     install commands + skill
  npx bug-bounty-workbench update [options]    re-install from the current version
  npx bug-bounty-workbench status              show what is installed
  npx bug-bounty-workbench uninstall [options] remove what setup wrote

Commands install with a bbw- prefix, so typing bbw in your agent lists all 25:
  /bbw-hunt  /bbw-programs  /bbw-scope  /bbw-recon  /bbw-surface
  /bbw-idor  /bbw-auth  /bbw-ssrf  /bbw-xss  /bbw-injection  /bbw-files
  /bbw-logic  /bbw-api  /bbw-graphql  /bbw-cloud  /bbw-secrets  /bbw-cache
  /bbw-takeover  /bbw-mobile  /bbw-ai  /bbw-chain  /bbw-score  /bbw-report
  /bbw-dedup  /bbw-submit

Options
  --agent=<name>   ${agentNames().join(' | ')}   (repeatable, comma-separated)
  --global, -g     install into the user-level directories instead of the project
  --project, -p    force project-level install (default when a marker exists)
  --dry-run, -n    print the plan, write nothing
  --json           machine-readable output
  --version, -v
  --help, -h

Nothing is installed outside these directories:
  claude    .claude/commands, .claude/skills/bug-bounty-workbench
  opencode  .opencode/command, .opencode/skill/bug-bounty-workbench
  cursor    .cursor/commands
  codex     ~/.codex/prompts (global only)

After installing, restart the agent and run:
  /bbw-hunt https://app.example.com "Acme" on Intigriti`);
}

function resolveScope(args, agent) {
  if (args.global) return 'global';
  if (args.project) return 'project';
  const spec = AGENTS[agent];
  if (!spec.project || (!spec.project.commands && !spec.project.skill)) return 'global';
  return 'project';
}

function scopeLabel(scope, plan) {
  if (scope === 'global') return 'global';
  const dir = plan.commandsDir ?? plan.skillDir;
  return `project (${dir})`;
}

function setup(args) {
  const home = os.homedir();
  const cwd = process.cwd();

  let agents = args.agents;
  if (!agents.length) agents = detectAgents({ cwd, fs });
  const detected = agents.length > 0;

  if (!agents.length) {
    console.error(
      `${red('No agent detected.')} Pass one explicitly:\n  npx ${PKG.name} setup --agent ${agentNames().join(' --agent ')}\n\nAvailable: ${agentNames().join(', ')}`,
    );
    return 1;
  }

  const unknown = agents.filter((name) => !AGENTS[name]);
  if (unknown.length) {
    console.error(`${red(`Unknown agent: ${unknown.join(', ')}`)}. Available: ${agentNames().join(', ')}`);
    return 1;
  }

  const results = [];
  for (const agent of agents) {
    const scope = resolveScope(args, agent);
    const plan = planInstall({ agent, scope, root: ROOT, cwd, home });
    const outcome = applyInstall(plan, { dryRun: args.dryRun });
    results.push({ agent, scope, plan, outcome });
  }

  if (args.json) {
    console.log(JSON.stringify({ version: PKG.version, results: results.map((r) => ({
      agent: r.agent,
      scope: r.scope,
      commands: r.plan.commandsDir,
      skill: r.plan.skillDir,
      files: r.outcome.files.length,
      dryRun: Boolean(args.dryRun),
    })) }, null, 2));
    return 0;
  }

  console.log(`${bold(`bug-bounty-workbench ${PKG.version}`)}  ${dim(detected ? 'agent detected' : 'agent specified')}\n`);

  for (const { agent, scope, plan, outcome } of results) {
    const spec = AGENTS[agent];
    console.log(`${bold(spec.label)}  ${dim(scopeLabel(scope, plan))}`);
    if (plan.commandsDir) {
      console.log(`  25 commands  -> ${plan.commandsDir}`);
    }
    if (plan.skillDir) console.log(`  method+skill -> ${plan.skillDir}`);
    console.log(`  files        ${outcome.files.length}${args.dryRun ? dim('  (dry run, nothing written)') : ''}`);
    console.log(`  next         ${spec.hint}\n`);
  }

  const first = AGENTS[results[0].agent];
  console.log(`${green('Done.')} ${first.hint}:`);
  console.log(`  /bbw-hunt https://app.example.com "Acme" on Intigriti\n`);
  console.log(dim(`Full index: ${path.join(ROOT, 'commands', 'README.md')}`));
  return 0;
}

/**
 * Re-apply every recorded install from the version now on disk.
 *
 * Reads the same manifests `setup` wrote, so it updates exactly the agents and
 * scopes that exist — no re-detection, no guessing, no touching a project that
 * never had an install. Files recorded by an earlier version but no longer
 * produced are removed, which is what makes a command rename safe.
 */
function update(args) {
  const home = os.homedir();
  const cwd = process.cwd();
  const scopes = args.global ? ['global'] : args.project ? ['project'] : ['project', 'global'];
  const jobs = [];

  for (const scope of scopes) {
    const manifestFile = path.join(scope === 'global' ? home : cwd, '.bbw-manifest.json');
    const record = readManifest(manifestFile);
    if (!record) continue;
    for (const entry of record.installs) {
      if (args.agents.length && !args.agents.includes(entry.agent)) continue;
      jobs.push({ scope, entry });
    }
  }

  if (!jobs.length) {
    const where = scopes.join(' or ');
    console.error(
      `${red('Nothing installed')} in ${where}. Run first:\n  npx ${PKG.name} setup${args.global ? ' --global' : ''}`,
    );
    return 1;
  }

  const results = [];
  for (const { scope, entry } of jobs) {
    const plan = planInstall({ agent: entry.agent, scope, root: ROOT, cwd, home });
    const outcome = applyInstall(plan, { dryRun: args.dryRun });
    results.push({ scope, agent: entry.agent, plan, outcome, from: entry.version ?? 'unknown' });
  }

  if (args.json) {
    console.log(JSON.stringify({ version: PKG.version, results: results.map((r) => ({
      agent: r.agent,
      scope: r.scope,
      from: r.from,
      to: PKG.version,
      files: r.outcome.files.length,
      removed: r.outcome.removed?.length ?? 0,
      dryRun: Boolean(args.dryRun),
    })) }, null, 2));
    return 0;
  }

  console.log(`${bold(`bug-bounty-workbench ${PKG.version}`)}  ${dim(args.dryRun ? 'update (dry run)' : 'update')}\n`);
  for (const { scope, agent, outcome, from } of results) {
    const spec = AGENTS[agent];
    const moved = from === 'unknown' || from === PKG.version ? '' : `  ${dim(`${from} ->`)} ${PKG.version}`;
    console.log(`${bold(spec.label)}  ${dim(scope)}${moved}`);
    console.log(`  files        ${outcome.files.length} written${outcome.removed?.length ? `, ${outcome.removed.length} stale removed` : ''}`);
    console.log(`  next         ${spec.hint}\n`);
  }

  console.log(dim(`Newer version available? npx ${PKG.name}@latest update`));
  return 0;
}

function status(args) {
  const home = os.homedir();
  const cwd = process.cwd();
  const rows = [];

  for (const scope of ['project', 'global']) {
    const manifestFile = path.join(scope === 'global' ? home : cwd, '.bbw-manifest.json');
    const record = readManifest(manifestFile);
    if (!record) continue;
    for (const entry of record.installs) {
      const present = entry.files.filter((file) => fs.existsSync(file)).length;
      rows.push({
        scope,
        agent: entry.agent,
        installedAt: entry.installedAt,
        files: entry.files.length,
        present,
        manifestFile,
      });
    }
  }

  if (args.json) {
    console.log(JSON.stringify({ version: PKG.version, installs: rows }, null, 2));
    return 0;
  }

  if (!rows.length) {
    console.log(`${bold(`bug-bounty-workbench ${PKG.version}`)}\n\nNothing installed here. Run:\n  npx ${PKG.name} setup`);
    return 0;
  }

  console.log(`${bold(`bug-bounty-workbench ${PKG.version}`)}\n`);
  for (const row of rows) {
    const healthy = row.present === row.files;
    console.log(
      `${healthy ? green('ok   ') : red('drift')} ${row.agent}  ${dim(row.scope)}  ${row.present}/${row.files} files  ${dim(row.installedAt)}`,
    );
    console.log(`      ${dim(row.manifestFile)}`);
  }
  return 0;
}

function uninstall(args) {
  const home = os.homedir();
  const cwd = process.cwd();
  const scopes = args.global ? ['global'] : args.project ? ['project'] : ['project', 'global'];
  let removed = 0;

  for (const scope of scopes) {
    const manifestFile = path.join(scope === 'global' ? home : cwd, '.bbw-manifest.json');
    const record = readManifest(manifestFile);
    if (!record) continue;

    const agents = args.agents.length
      ? record.installs.filter((entry) => args.agents.includes(entry.agent))
      : record.installs;
    if (!agents.length) continue;

    for (const entry of agents) {
      const outcome = removeInstall(manifestFile, { dryRun: args.dryRun, agent: entry.agent });
      removed += outcome.removed.length;
      console.log(
        `${args.dryRun ? 'would remove' : 'removed'} ${outcome.removed.length} files (${entry.agent}, ${scope})`,
      );
    }
  }

  if (!removed) console.log('Nothing to remove here.');
  return 0;
}

const args = parseArgs(process.argv.slice(2));

if (args.version) {
  console.log(PKG.version);
  process.exit(0);
}
if (args.help || args._[0] === 'help') {
  help();
  process.exit(0);
}

const command = args._[0] ?? 'setup';
let code = 0;
if (command === 'setup' || command === 'install') code = setup(args);
else if (command === 'update' || command === 'upgrade') code = update(args);
else if (command === 'status' || command === 'list') code = status(args);
else if (command === 'uninstall' || command === 'remove') code = uninstall(args);
else {
  console.error(`Unknown command: ${command}\n`);
  help();
  code = 1;
}
process.exit(code);
