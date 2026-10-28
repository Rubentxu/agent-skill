/**
 * Pure semantic kernel: no filesystem, CLI, Git, configuration writes or LLM calls.
 * Event fields are data, never instructions to the hook.
 */
export type HookCall = {
  tool_name?: unknown;
  tool_input?: unknown;
  tool_response?: unknown;
};
export type HookInput = {
  hook_event_name?: unknown;
  session_id?: unknown;
  cwd?: unknown;
  agent_id?: unknown;
  tool_name?: unknown;
  tool_input?: unknown;
  tool_response?: unknown;
  tool_calls?: unknown;
  stop_hook_active?: unknown;
};
export type State = {
  read: string[];
  changed: string[];
  seen: string[];
  delivered: string[];
  taskId?: string;
};
export const emptyState = (): State => ({ read: [], changed: [], seen: [], delivered: [] });
const SOURCE = /\.(?:rs|kt|kts|java|scala|go|py|ts|tsx|js|jsx|mjs|cjs|c|h|cc|cpp|hpp|cs|swift|dart|php)$/i;
const IGNORE = /(^|\/)(?:\.git|node_modules|vendor|target|build|dist|coverage|\.next|backlog|\.backlog|groma|\.groma|\.env[^/]*)(\/|$)/i;
const TASK_ID = /^[A-Za-z][A-Za-z0-9_.-]{0,63}$/;
export const validTaskId = (id: unknown): id is string => typeof id === "string" && TASK_ID.test(id);
export const sourcePath = (file: string): boolean =>
  SOURCE.test(file) && !IGNORE.test(file) && !file.includes("\0");
export const boundedPush = (list: string[], value: string, max = 64): string[] =>
  list.includes(value) ? list : [...list, value].slice(-max);
export const asRecord = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null;
export const inputPath = (value: unknown): string | undefined => {
  const object = asRecord(value);
  const file = object?.file_path ?? object?.notebook_path;
  return typeof file === "string" && file.length <= 4096 ? file : undefined;
};
export const changedFile = (event: HookInput): string | undefined =>
  event.hook_event_name === "PostToolUse" &&
    ["Write", "Edit", "MultiEdit", "NotebookEdit"].includes(String(event.tool_name))
    ? inputPath(event.tool_input) : undefined;
export const readCalls = (event: HookInput): string[] =>
  event.hook_event_name === "PostToolBatch" && Array.isArray(event.tool_calls)
    ? [...new Set(event.tool_calls.slice(0, 100)
      .filter((entry: unknown) => {
        const item = asRecord(entry);
        // Trust only successful-looking Read calls; never parse response content as commands.
        return item?.tool_name === "Read" &&
          item?.tool_response !== undefined && item?.is_error !== true;
      })
      .map((entry: unknown) => inputPath(asRecord(entry)?.tool_input))
      .filter((x: unknown): x is string => typeof x === "string"))].slice(0, 8)
    : [];
export type Recommendation =
  | { kind: "architecture"; file: string; owner: string; parent?: string }
  | { kind: "trace"; files: string[]; taskId?: string }
  | { kind: "inspect"; taskId?: string };
export const recommendTrace = (state: State): Recommendation | null =>
  state.changed.length > 0
    ? { kind: "trace", files: state.changed.slice(-5), taskId: state.taskId } : null;
export const safeGromaOwner = (output: string): { owner: string; parent?: string } | null => {
  // Only extract source-owned stable ids. Never pass arbitrary Markdown descriptions to Claude.
  const lines = output.split(/\r?\n/).slice(0, 24);
  const line = lines.find(x => /^\s*[A-Za-z][A-Za-z0-9_.-]{0,79}  component  /i.test(x));
  if (!line) return null;
  const owner = line.trim().split(/\s{2,}/)[0];
  if (!validTaskId(owner)) return null;
  const parent = lines.find(x => /^parent: [A-Za-z][A-Za-z0-9_.-]{0,79}$/.test(x))?.slice(8);
  return { owner, ...(parent ? { parent } : {}) };
};
export function presentation(recommendation: Recommendation): string {
  switch (recommendation.kind) {
    case "architecture":
      return "Groma (lectura, no modificación): " + JSON.stringify(recommendation.file) +
        " pertenece al componente " + JSON.stringify(recommendation.owner) +
        (recommendation.parent ? " (padre: " + JSON.stringify(recommendation.parent) + ")" : "") +
        ". Usa groma view <ruta> para inspeccionar relaciones; esta lectura NO implica modifiedFiles.";
    case "trace":
      return "Backlog (reconciliación sugerida, NO ejecutada): cambios observados en " +
        recommendation.files.map(x => JSON.stringify(x)).join(", ") + ". " +
        (recommendation.taskId ? "Relee backlog task view " + recommendation.taskId + " --json. " :
          "Identifica la tarea real mediante backlog task list --json; no supongas un ID activo. ") +
        "Si procede, actualiza modifiedFiles con TODAS las rutas actuales y las nuevas; --modified-file reemplaza la lista. " +
        "Revisa notas, AC/DoD y gates antes de transicionar. No marques Done automáticamente.";
    case "inspect":
      return "Backlog: comprueba estado y dependencias mediante CLI; al detectar un bug fuera del alcance, " +
        "clasifícalo como corrección dentro de la tarea, borrador, ticket independiente o descarte razonado, " +
        "sin crear tareas ni modificar estados desde este hook.";
  }
}
export const outputContext = (event: string, value: string): Record<string, unknown> => ({
  hookSpecificOutput: { hookEventName: event, additionalContext: value.slice(0, 1300) },
});
