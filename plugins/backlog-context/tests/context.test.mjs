import test from "node:test";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { chmodSync } from "node:fs";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, symlinkSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { changedFile, readCalls, safeGromaOwner, presentation, emptyState, boundedPush } from "../src/kernel.ts";
import { handleEvent, repoFile } from "../src/hook.ts";

function fixture() {
  const root = mkdtempSync(join(tmpdir(), "backlog-hook-test-"));
  mkdirSync(join(root, "src"));
  mkdirSync(join(root, "backlog"));
  writeFileSync(join(root, "src", "example.ts"), "export const result = 1;");
  writeFileSync(join(root, "backlog", "config.yml"), "projectName: sample");
  const data = mkdtempSync(join(tmpdir(), "backlog-context-state-"));
  const env = { CLAUDE_PROJECT_DIR: root, CLAUDE_PLUGIN_DATA: data };
  const event = hook_event_name => ({ hook_event_name, cwd: root, session_id: "session-1" });
  return { root, data, env, event, file: join(root, "src", "example.ts") };
}
test("safe owner parser extracts stable ids, not untrusted descriptions", () => {
  assert.deepEqual(safeGromaOwner("Owner\n-----\npipeline-exec  component  Useful title\nparent: execution\n"), { owner: "pipeline-exec", parent: "execution" });
  assert.equal(safeGromaOwner("no owner: src/example.ts"), null);
  assert.equal(safeGromaOwner("Owner\n-----\n<script>  component  evil"), null);
});
test("only real source paths within project, including symlink check", () => {
  const f = fixture();
  assert.equal(repoFile(f.root, f.file), "src/example.ts");
  assert.equal(repoFile(f.root, "../elsewhere.ts"), null);
  assert.equal(repoFile(f.root, join(f.root, "backlog", "config.yml")), null);
  const outsider = mkdtempSync(join(tmpdir(), "outside-hook-"));
  const external = join(outsider, "other.ts");
  writeFileSync(external, "secret");
  symlinkSync(external, join(f.root, "src", "outside.ts"));
  assert.equal(repoFile(f.root, join(f.root, "src", "outside.ts")), null);
});
test("read-only batch accepts only Read, never guesses paths from shell text", () => {
  const e = {hook_event_name:"PostToolBatch",tool_calls:[
    {tool_name:"Read",tool_input:{file_path:"src/example.ts"},tool_response:"some code"},
    {tool_name:"Bash",tool_input:{command:"cat /etc/shadow"},tool_response:"secret"},
    {tool_name:"Read",tool_input:{file_path:"src/example.ts"},tool_response:"another code"}
  ]};
  assert.deepEqual(readCalls(e), ["src/example.ts"]);
  assert.deepEqual(readCalls({hook_event_name:"PostToolBatch",tool_calls:[{tool_name:"Read",tool_input:{file_path:"x.ts"},is_error:true,tool_response:"fail"}]}), []);
});
test("failed writes never become modifiedFiles", () => {
  const f=fixture();
  const failed={...f.event("PostToolUseFailure"),tool_name:"Edit",tool_input:{file_path:f.file}};
  assert.equal(handleEvent(failed,f.env),null);
  assert.equal(existsSync(join(f.data,"sessions")),false);
  assert.equal(changedFile(failed),undefined);
});
test("session init only hints at CLI, never changes backlog", () => {
  const f=fixture();
  const old=readFileSync(join(f.root,"backlog","config.yml"),"utf8");
  const response=handleEvent(f.event("SessionStart"),f.env);
  assert.match(response.hookSpecificOutput.additionalContext,/backlog task list --json/);
  assert.equal(handleEvent(f.event("SessionStart"),f.env),null);
  assert.equal(readFileSync(join(f.root,"backlog","config.yml"),"utf8"),old);
});
test("successful edit remains internal until batch, then recommends full list",()=>{
  const f=fixture();
  assert.equal(handleEvent({...f.event("PostToolUse"),tool_name:"Edit",tool_input:{file_path:f.file}},f.env),null);
  const batch=handleEvent({...f.event("PostToolBatch"),tool_calls:[]},f.env);
  assert.equal(batch.hookSpecificOutput.hookEventName,"PostToolBatch");
  assert.match(batch.hookSpecificOutput.additionalContext,/modifiedFiles/);
  assert.match(batch.hookSpecificOutput.additionalContext,/No marques Done automáticamente/);
  assert.equal(handleEvent({...f.event("PostToolBatch"),tool_calls:[]},f.env),null);
  assert.equal(handleEvent(f.event("Stop"),f.env),null);
});
test("stop emits at most one reminder and honors stop_hook_active",()=>{
  const f=fixture();
  handleEvent({...f.event("PostToolUse"),tool_name:"Write",tool_input:{file_path:f.file}},f.env);
  assert.equal(handleEvent({...f.event("Stop"),stop_hook_active:true},f.env),null);
  const s=handleEvent(f.event("Stop"),f.env);
  assert.equal(s.hookSpecificOutput.hookEventName,"Stop");
  assert.equal(s.decision,undefined);
  assert.equal(handleEvent(f.event("Stop"),f.env),null);
});
test("missing persistent directory leaves no project-side state",()=>{
  const f=fixture();
  assert.equal(handleEvent({...f.event("PostToolUse"),tool_name:"Edit",tool_input:{file_path:f.file}},{CLAUDE_PROJECT_DIR:f.root}),null);
  assert.equal(existsSync(join(f.root,".claude")),false);
});
test("explicit task ID is included only if well formed",()=>{
  const f=fixture();
  const ok=handleEvent(f.event("SessionStart"),{...f.env,BACKLOG_CONTEXT_TASK_ID:"TASK-12"});
  assert.match(ok.hookSpecificOutput.additionalContext,/TASK-12/);
  const g=fixture();
  const bad=handleEvent(g.event("SessionStart"),{...g.env,BACKLOG_CONTEXT_TASK_ID:"TASK-12; rm -rf ."});
  assert.doesNotMatch(bad.hookSpecificOutput.additionalContext,/rm -rf/);
});
test("session end deletes plugin state but not project files",()=>{
  const f=fixture();
  handleEvent(f.event("SessionStart"),f.env);
  handleEvent(f.event("SessionEnd"),f.env);
  assert.equal(handleEvent(f.event("SessionStart"),f.env)?.hookSpecificOutput.hookEventName,"SessionStart");
  assert.equal(existsSync(f.file),true);
});
test("kernel deterministic and bounded",()=>{
  assert.deepEqual(emptyState(),emptyState());
  let paths=[];
  for(let i=0;i<90;i++) paths=boundedPush(paths,"path-"+i);
  assert.equal(paths.length,64);
  assert.equal(boundedPush(paths,"path-89").length,64);
  assert.match(presentation({kind:"inspect"}),/sin crear tareas/);
});
test("plugin state never writes into consumer project when data env misconfigured",()=>{
  const f=fixture();
  const env={CLAUDE_PROJECT_DIR:f.root, CLAUDE_PLUGIN_DATA:join(f.root,".claude")};
  const result=handleEvent(f.event("SessionStart"),env);
  assert.match(result.hookSpecificOutput.additionalContext,/backlog task list/);
  assert.equal(existsSync(join(f.root,".claude")),false);
});
test("Groma adapter enriches a file read without scanning or writing Backlog",()=>{
  if (process.platform === "win32") return;
  const f=fixture();
  mkdirSync(join(f.root,"groma"));
  writeFileSync(join(f.root,"groma","config.json"),'{"version":"1"}');
  const bin=mkdtempSync(join(tmpdir(),"fake-groma-bin-"));
  const cmd=join(bin,"groma");
  writeFileSync(cmd,"#!/bin/sh\\nprintf '%s\\n' 'Owner' '-----' 'component-42  component  Safe' 'parent: system-root'\\n");
  chmodSync(cmd,0o755);
  const before=readFileSync(join(f.root,"backlog","config.yml"),"utf8");
  const original=process.env.PATH;
  try {
    process.env.PATH=bin+":"+original;
    const result=handleEvent({...f.event("PostToolBatch"),tool_calls:[{
      tool_name:"Read",tool_input:{file_path:f.file},tool_response:"file contents"
    }]},f.env);
    assert.match(result.hookSpecificOutput.additionalContext,/component-42/);
    assert.match(result.hookSpecificOutput.additionalContext,/lectura, no modificación/);
    assert.equal(readFileSync(join(f.root,"backlog","config.yml"),"utf8"),before);
  } finally {process.env.PATH=original;}
});
test("standalone hook reads real stdin JSON and prints valid Claude context",()=>{
  const f=fixture();
  const executable=fileURLToPath(new URL("../src/hook.ts",import.meta.url));
  const run=spawnSync(process.execPath,["--experimental-strip-types",executable],{
    input:JSON.stringify(f.event("SessionStart")),
    env:{...process.env,...f.env},encoding:"utf8",timeout:3000
  });
  assert.equal(run.status,0,run.stderr);
  const output=JSON.parse(run.stdout);
  assert.equal(output.hookSpecificOutput.hookEventName,"SessionStart");
  assert.match(output.hookSpecificOutput.additionalContext,/backlog task list/);
});
test("malformed contexts and unknown events fail open",()=>{
  const f=fixture();
  assert.equal(handleEvent({hook_event_name:"TaskCompleted",cwd:f.root,session_id:"session-1"},f.env),null);
  assert.equal(handleEvent({hook_event_name:"PostToolBatch",cwd:"/tmp",session_id:"session-1"},f.env),null);
  assert.equal(handleEvent({hook_event_name:"PostToolBatch",cwd:f.root,session_id:"../../bad"},f.env),null);
});
