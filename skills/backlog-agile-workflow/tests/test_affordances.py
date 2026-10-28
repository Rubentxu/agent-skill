import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("backlog_agile_router", ROOT / "scripts/affordances.py")
router = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = router
spec.loader.exec_module(router)


def state(intent="triage", mode="read", task=None, config=None, **kwargs):
    d = {"intent": intent, "cli": "available", "project": "initialized", "basis": "observed",
         "mode": mode, "task": task if task is not None else {"id": "TASK-7", "isReady": True,
                                                       "archived": False},
         "config": config if config is not None else {"autoCommit": False, "remoteOperations": False,
                                                      "bypassGitHooks": False, "onStatusChange": False}}
    d.update(kwargs)
    return d


class RouterTests(unittest.TestCase):
    def test_catalog_includes_planned_but_does_not_load_it(self):
        o = router.affordances({"intent": "catalog"})
        self.assertIn({"id": "sprint-forecast", "status": "planned"}, o["available"])
        self.assertEqual(o["_links"], [])

    def test_missing_cli_does_not_offer_install_command(self):
        o = router.affordances(state(cli="missing"))
        self.assertEqual(o["decision"], "DISCOVER")
        self.assertEqual(o["_links"][0]["rel"], "inspect-cli")
        self.assertNotIn("npx backlog ", json.dumps(o))

    def test_absent_project_never_initializes(self):
        o = router.affordances(state(project="absent", intent="capture", mode="apply"))
        self.assertEqual(o["decision"], "DISCOVER")
        self.assertFalse(any(l["rel"] == "propose-cli-write" for l in o["_links"]))

    def test_unobserved_requires_inspection(self):
        o = router.affordances(state(basis="unknown"))
        self.assertEqual(o["decision"], "INSPECT_MORE")

    def test_stale_does_not_reuse_context(self):
        o = router.affordances(state(basis="stale"))
        self.assertEqual(o["_links"][0]["rel"], "refresh-basis")

    def test_triage_is_read_only_and_loads_only_one_lens(self):
        o = router.affordances(state())
        self.assertEqual(o["decision"], "READY")
        self.assertEqual(o["lenses"], ["triage"])
        self.assertEqual(o["suggested_reads"][1], ["backlog", "task", "list", "--json"])

    def test_triage_requires_ready_when_candidate_known(self):
        o = router.affordances(state(task={"id": "TASK-2", "isReady": False}))
        self.assertEqual(o["decision"], "INSPECT_MORE")

    def test_execute_requires_ready_dependency_verdict(self):
        o = router.affordances(state(intent="execute", task={"id": "TASK-2"}))
        self.assertEqual(o["decision"], "INSPECT_MORE")
        self.assertEqual(o["_links"][-1]["rel"], "inspect-dependencies")

    def test_execute_uses_exact_safe_task_id_without_shell(self):
        o = router.affordances(state(intent="execute"))
        self.assertEqual(o["suggested_reads"][-1], ["backlog", "task", "view", "TASK-7", "--json"])

    def test_malicious_task_id_rejected(self):
        with self.assertRaises(ValueError):
            router.affordances(state(intent="execute", task={"id": "TASK-1; rm -rf /", "isReady": True}))

    def test_archived_task_cannot_be_edited(self):
        o = router.affordances(state(intent="execute", mode="apply", task={"id": "TASK-3", "isReady": True, "archived": True}))
        self.assertEqual(o["decision"], "BLOCKED")

    def test_close_incomplete_ac_is_blocked(self):
        o = router.affordances(state(intent="close", mode="apply", task={"id": "TASK-7", "archived": False,
            "acceptanceCriteriaCount": 3, "acceptanceCriteriaCompleted": 2,
            "definitionOfDoneCount": 2, "definitionOfDoneCompleted": 2}))
        self.assertEqual(o["decision"], "BLOCKED")
        self.assertIn("complete-checklist", [x["rel"] for x in o["_links"]])

    def test_close_unknown_dod_requires_inspection(self):
        o = router.affordances(state(intent="close", mode="apply", task={"id": "TASK-7", "archived": False,
            "acceptanceCriteriaCount": 3, "acceptanceCriteriaCompleted": 3}))
        self.assertEqual(o["decision"], "INSPECT_MORE")

    def test_ready_close_does_not_execute(self):
        o = router.affordances(state(intent="close", mode="apply", task={"id": "TASK-7", "archived": False,
            "acceptanceCriteriaCount": 2, "acceptanceCriteriaCompleted": 2,
            "definitionOfDoneCount": 2, "definitionOfDoneCompleted": 2}))
        self.assertEqual(o["decision"], "AUTHORIZED_ACTION")
        self.assertEqual(o["status"], "NAVIGATION_ONLY")

    def test_proposal_never_changes_task(self):
        o = router.affordances(state(intent="capture", mode="propose"))
        self.assertEqual(o["decision"], "PROPOSE_ONLY")

    def test_auto_commit_requires_side_effect_acknowledgement(self):
        config={"autoCommit": True, "remoteOperations": False, "bypassGitHooks": False, "onStatusChange": False}
        o=router.affordances(state(intent="execute", mode="apply", config=config))
        self.assertEqual(o["decision"], "BLOCKED")
        self.assertIn("autoCommit", o["warnings"][0])
        config2=router.affordances(state(intent="execute", mode="apply", config=config, effects_acknowledged=True))
        self.assertEqual(config2["decision"], "AUTHORIZED_ACTION")

    def test_callbacks_must_be_acknowledged(self):
        c={"autoCommit": False, "remoteOperations": False, "bypassGitHooks": False, "onStatusChange": True}
        self.assertEqual(router.affordances(state(intent="close", mode="apply", config=c, task={"id": "TASK-7",
            "acceptanceCriteriaCount": 0,"acceptanceCriteriaCompleted": 0,
            "definitionOfDoneCount": 0,"definitionOfDoneCompleted": 0}))['decision'], "BLOCKED")

    def test_unknown_config_fails_closed_on_write(self):
        o = router.affordances(state(intent="capture", mode="apply", config={}))
        self.assertEqual(o["decision"], "INSPECT_MORE")
        self.assertIn("inspect-configuration", [l['rel'] for l in o['_links']])

    def test_read_only_permitted_with_unknown_config(self):
        self.assertEqual(router.affordances(state(intent="capture", mode="read", config={}))['decision'], "READY")

    def test_available_skill_delegation_only(self):
        self.assertNotIn("delegate-skill", [l['rel'] for l in router.affordances(state(intent="verify"))['_links']])
        o=router.affordances(state(intent="verify",available_skills=["delivery-first-testing"]))
        self.assertEqual([l['skill_id'] for l in o['_links'] if l['rel']=="delegate-skill"], ["delivery-first-testing"])

    def test_unknown_skill_never_emits_delegate(self):
        o=router.affordances(state(intent="execute",available_skills=["absent-tool"]))
        self.assertNotIn("delegate-skill", [l['rel'] for l in o['_links']])

    def test_no_leaked_state_between_turns(self):
        base=state(intent="capture")
        first=router.affordances(base)
        router.affordances(state(intent="execute",mode="apply"))
        self.assertEqual(first,router.affordances(base))

    def test_all_ready_lenses_exist_and_contained(self):
        for x in router._registry("lens-registry.json", "lenses"):
            if x['status'] == 'ready':
                path=(ROOT/x['playbook']).resolve()
                self.assertTrue(path.is_file())
                self.assertTrue(path.is_relative_to(ROOT.resolve()))

    def test_all_session_examples_parse(self):
        for name in ("triage.json", "close-blocked.json", "config-risk.json", "uninitialized.json"):
            with self.subTest(name=name):
                o=router.affordances(json.loads((ROOT/"examples"/name).read_text()))
                self.assertEqual(o['status'], 'NAVIGATION_ONLY')

    def test_inputs_fail_closed_on_types(self):
        for bad in ({'mode':'write'}, {'task': {'archived': 1}}, {'config': {'autoCommit': 'yes'}},
                    {'available_skills': ['x','x']}, {'extra_field': 'unused'}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                router.affordances({**state(), **bad})


if __name__ == '__main__':
    unittest.main()
