/**
 * Claude Code adapter for the pure recommendation kernel.
 * Read-only integration: never runs backlog, groma scan, or a mutation.
 * Node >=22 required for --experimental-strip-types.
 */
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import {
  existsSync, mkdirSync, readFileSync, realpathSync, renameSync, rmSync,
  openSync, closeSync, writeFileSync,
} from "node:fs";
import { join, resolve, relative, isAbsolute, sep } from "node:path";
import { emptyState, boundedPush, changedFile, readCalls, sourcePath,
  safeGromaOwner, validTaskId, presentation, recommendTrace, outputContext,
  type HookInput, type State } from "./kernel.ts";

type Runtime = {
  root: string;
  stateFile?: string;
  taskId?: string;
  cwd: string;
};
const DATA_ENV = "CLAUDE_PLUGIN_DATA";
const MAX_INPUT = 250_000;
const MAX_STATE = 10_000;
const isWithin = (root: string, target: string): boolean => {
  const diff = relative(root, target);
  return diff !== "" && diff !== ".." && !diff.startsWith(".." + sep) && !isAbsolute(diff);
};
export function repoFile(root: string, candidate: string): string | null {
  if (!candidate || candidate.length > 4096 || candidate.includes("\0")) return null;
  const abs = resolve(root, candidate);
  if (!isWithin(root, abs)) return null;
  let actual: string;
  try { actual = realpathSync(abs); } catch { return null; }
  if (!isWithin(root, actual)) return null;
  const rel = relative(root, actual).split(sep).join("/");
  return sourcePath(rel) ? rel : null;
}
function loadRuntime(event: HookInput, env: NodeJS.ProcessEnv): Runtime | null {
  const rawRoot = env.CLAUDE_PROJECT_DIR;
  const session = event.session_id;
  if (!rawRoot || typeof session !== "string" || !/^[a-zA-Z0-9_-]{1,128}$/.test(session)) return null;
  let root: string;
  try { root = realpathSync(rawRoot); } catch { return null; }
  const cwd = typeof event.cwd === "string" && event.cwd.length < 4096 ? event.cwd : root;
  let actualCwd: string;
  try { actualCwd = realpathSync(cwd); } catch { return null; }
  if (actualCwd !== root && !isWithin(root, actualCwd)) return null;
  const taskId = validTaskId(env.BACKLOG_CONTEXT_TASK_ID) ? env.BACKLOG_CONTEXT_TASK_ID : undefined;
  const data = env[DATA_ENV];
  if (!data || !isAbsolute(data)) return { root, cwd: actualCwd, taskId };
  const key = createHash("sha256").update(JSON.stringify([root, session, event.agent_id ?? "main"])).digest("hex");
  return { root, cwd: actualCwd, stateFile: join(data, "sessions", key + ".json"), taskId };
}
function readState(file?: string): State {
  if (!file) return emptyState();
  try {
    const raw = readFileSync(file, "utf8");
    if (raw.length > MAX_STATE) return emptyState();
    const value = JSON.parse(raw);
    const safeArray = (x: unknown): string[] =>
      Array.isArray(x) ? x.filter(v => typeof v === "string" && v.length < 4100).slice(-64) : [];
    return { read: safeArray(value.read), changed: safeArray(value.changed),
      seen: safeArray(value.seen), delivered: safeArray(value.delivered),
      taskId: validTaskId(value.taskId) ? value.taskId : undefined };
  } catch { return emptyState(); }
}
function updateState(runtime: Runtime, fn: (state: State) => { state: State; context?: string }): string | undefined {
  if (!runtime.stateFile) return fn(emptyState()).context;
  const path = runtime.stateFile;
  try { mkdirSync(join(path, ".."), { recursive: true, mode: 0o700 }); } catch { return; }
  // Atomic exclusive lock. Another concurrent hook may skip this event; never clobber its state.
  const lock = path + ".lock";
  let fd: number;
  try { fd = openSync(lock, "wx", 0o600); } catch { return; }
  try {
    const state = readState(path);
    if (runtime.taskId) state.taskId = runtime.taskId;
    const result = fn(state);
    const tmp = path + "." + process.pid + ".tmp";
    try {
      writeFileSync(tmp, JSON.stringify(result.state), { mode: 0o600 });
      renameSync(tmp, path);
    } finally { rmSync(tmp, { force: true }); }
    return result.context;
  } catch { return; }
  finally { closeSync(fd); rmSync(lock, { force: true }); }
}
function gromaInstalled(root: string): boolean =>
  existsSync(join(root, "groma", "config.json")) || existsSync(join(root, ".groma", "config.json"));
export function queryOwner(root: string, file: string): {owner: string;parent?: string}|null {
  if (!gromaInstalled(root)) return null;
  const result = spawnSync("groma", ["view", file], {
    cwd: root, encoding: "utf8", timeout: 1500, maxBuffer: 20000,
    windowsHide: true, stdio: ["ignore", "pipe", "ignore"],
  });
  if (result.error || result.status !== 0 || typeof result.stdout !== "string") return null;
  return safeGromaOwner(result.stdout);
}
export function handleEvent(event: HookInput, env: NodeJS.ProcessEnv = process.env): Record<string, unknown> | null {
  const kind = event.hook_event_name;
  if (!["SessionStart","PostToolBatch","PostToolUse","PostToolUseFailure","Stop","SessionEnd"].includes(String(kind))) return null;
  const runtime = loadRuntime(event, env);
  if (!runtime) return null;
  if (kind === "SessionEnd") {
    if (runtime.stateFile) {
      rmSync(runtime.stateFile, { force: true });
    }
    return null;
  }
  if (kind === "PostToolUse") {
    const candidate = changedFile(event);
    if (candidate) {
      const file = repoFile(runtime.root, candidate);
      if (file) updateState(runtime, state => ({
        state: { ...state, changed: boundedPush(state.changed, file) },
      }));
    }
    return null;
  }
  if (kind === "PostToolUseFailure") return null; // Failure is not proof of a write.
  if (kind === "PostToolBatch") {
    const candidates = readCalls(event).map(x => repoFile(runtime.root, x))
      .filter((x): x is string => x !== null);
    const context = updateState(runtime, state => {
      const first = candidates.find(file => !state.read.includes(file));
      const changedNow = state.changed.filter(file => !state.delivered.includes("trace:" + file));
      for (const file of candidates) state.read = boundedPush(state.read, file);
      let message: string | undefined;
      if (first && !state.seen.includes("owner:" + first)) {
        state.seen = boundedPush(state.seen, "owner:" + first);
        const owner = queryOwner(runtime.root, first);
        if (owner) message = presentation({ kind: "architecture", file: first, ...owner });
      }
      if (changedNow.length) {
        const advice = recommendTrace({ ...state, changed: changedNow });
        if (advice) message = [message, presentation(advice)].filter(Boolean).join("\n");
        for (const file of changedNow) state.delivered = boundedPush(state.delivered, "trace:" + file);
      }
      return { state, context: message };
    });
    return context ? outputContext("PostToolBatch", context) : null;
  }
  if (kind === "Stop") {
    if (event.stop_hook_active === true) return null;
    // One reminder only if PostToolBatch did not already report the changed files.
    const context = updateState(runtime, state => {
      const pending = state.changed.filter(f => !state.delivered.includes("trace:" + f));
      if (pending.length === 0) return { state };
      for (const file of pending) state.delivered = boundedPush(state.delivered, "trace:" + file);
      const recommendation = recommendTrace({ ...state, changed: pending });
      return { state, context: recommendation ? presentation(recommendation) : undefined };
    });
    return context ? outputContext("Stop", context) : null;
  }
  if (kind === "SessionStart") {
    const context = updateState(runtime, state => {
      if (state.delivered.includes("session")) return { state };
      state.delivered = boundedPush(state.delivered, "session");
      if (!existsSync(join(runtime.root, "backlog")) &&
          !existsSync(join(runtime.root, ".backlog")) &&
          !existsSync(join(runtime.root, "backlog.config.yml"))) return { state };
      return { state, context: state.taskId
        ? "Backlog contextual: tarea seleccionada por BACKLOG_CONTEXT_TASK_ID=" + state.taskId +
          ". Comprueba backlog task view " + state.taskId + " --json antes de actualizar; el hook no ejecuta CLI."
        : "Backlog contextual disponible. No se ha identificado inequívocamente una tarea activa; usa backlog task list --json y consulta readiness antes de empezar. Ningún estado se cambia por el hook." };
    });
    return context ? outputContext("SessionStart", context) : null;
  }
  return null;
}
async function main(): Promise<void> {
  let raw = "";
  for await (const chunk of process.stdin) {
    raw += String(chunk);
    if (raw.length > MAX_INPUT) return;
  }
  try {
    const event = JSON.parse(raw) as HookInput;
    const response = handleEvent(event);
    if (response) process.stdout.write(JSON.stringify(response) + "\n");
  } catch { /* Fail open: never block Claude on malformed hook payloads. */ }
}
// Explicit test import guard; CLI executes only when invoked as the hook command.
if (process.argv[1] && import.meta.url === new URL("file://" + resolve(process.argv[1])).href) {
  await main();
}
