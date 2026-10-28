"""Unit tests for deterministic, non-writing reconciliation of specification packets."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("backlog_spec_projection", ROOT / "scripts/spec_projection.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def fixtures():
    p = json.loads((ROOT / "examples/spec-packet.json").read_text())
    s = json.loads((ROOT / "examples/spec-existing-tasks.json").read_text())
    return p, s


class SpecProjectionTests(unittest.TestCase):
    def test_discover_specification_without_backlog_cli(self):
        from importlib.util import spec_from_file_location, module_from_spec
        spec = spec_from_file_location("spec_routing", ROOT / "scripts/affordances.py")
        router = module_from_spec(spec); spec.loader.exec_module(router)
        r = router.affordances({"intent":"specify", "cli":"missing",
               "project":"absent", "basis":"observed", "mode":"propose"})
        self.assertEqual(r["decision"], "PROPOSE_ONLY")
        self.assertIn("specification-intake", r["lenses"])
        self.assertEqual(r["suggested_reads"], [])

    def test_reconciliation_without_backlog_cli_requires_discovery(self):
        from importlib.util import spec_from_file_location, module_from_spec
        spec = spec_from_file_location("sync_routing", ROOT / "scripts/affordances.py")
        router = module_from_spec(spec); spec.loader.exec_module(router)
        r = router.affordances({"intent":"sync-specs", "cli":"missing",
               "project":"absent", "basis":"observed", "mode":"propose"})
        self.assertEqual(r["decision"], "DISCOVER")

    def test_historical_block_kept_and_new_deps_ordered(self):
        p, s = fixtures()
        r = module.project(p,s)
        self.assertEqual(r['kind'], 'backlog-projection')
        self.assertEqual(r['status'], 'PROPOSAL_ONLY')
        a = {x['key']:x for x in r['actions']}
        self.assertEqual(a['R0.W1']['disposition'],'PRESERVE_ARCHIVED')
        self.assertEqual(a['R1.W1']['disposition'],'PROPOSE_CREATE')
        self.assertEqual(a['R1.W2']['disposition'],'WAIT_FOR_DEPENDENCY_IDS')
        self.assertEqual(a['R1.W2']['pendingDependencyKeys'],['R1.W1'])
        self.assertEqual([x['key'] for x in r['actions']],['R0.W1','R1.W1','R1.W2'])

    def test_repeat_is_deterministic_and_never_mutates_inputs(self):
        p, s=fixtures(); pb,sb=copy.deepcopy(p),copy.deepcopy(s)
        self.assertEqual(module.project(p,s),module.project(p,s))
        self.assertEqual((p,s),(pb,sb))

    def test_same_ref_never_creates_second_task(self):
        p,s=fixtures()
        s['tasks'].append({'id':'TASK-9','title':'Consulta verificable',
                           'references':['docs/ROADMAP.md#R1.W1']})
        result=module.project(p,s)
        task=next(x for x in result['actions'] if x['key']=='R1.W1')
        self.assertEqual(task['disposition'],'REVIEW_EXISTING')
        self.assertEqual(task['existingTaskId'],'TASK-9')

    def test_archived_task_must_not_be_updated(self):
        p,s=fixtures()
        p['tasks'][0]['state']='active'
        r=module.project(p,s)
        a=next(x for x in r['actions'] if x['key']=='R0.W1')
        self.assertEqual(a['disposition'], 'PRESERVE_ARCHIVED')
        self.assertTrue(any('read-only' in x for x in r['warnings']))

    def test_documentary_done_without_receipt_warns(self):
        p,s=fixtures()
        p['tasks'][0]['evidenceRefs']=[]
        r=module.project(p,s)
        self.assertTrue(any('without receipt' in w for w in r['warnings']))

    def test_unknown_title_collision_needs_review(self):
        p,s=fixtures();s['tasks'].append({'id':'TASK-9','title':'Consulta verificable','references':[]})
        result=module.project(p,s)
        task=next(x for x in result['actions'] if x['key']=='R1.W1')
        self.assertEqual(task['disposition'],'REVIEW_POSSIBLE_DUPLICATE')
        self.assertEqual(task['possibleDuplicateIds'],['TASK-9'])

    def test_incomplete_snapshot_never_proposes_creation(self):
        p,s=fixtures();p['snapshotScope']='filtered'
        r=module.project(p,s)
        self.assertEqual(next(x for x in r['actions'] if x['key']=='R1.W1')['disposition'],'NEEDS_CORPUS')

    def test_no_snapshot_never_proposes_creation(self):
        p,_=fixtures();r=module.project(p,None)
        self.assertNotIn('PROPOSE_CREATE',{x['disposition'] for x in r['actions']})

    def test_duplicate_source_identity_rejected(self):
        p,s=fixtures();p['tasks'][1]['sourceRef']=p['tasks'][0]['sourceRef']
        with self.assertRaises(ValueError):module.project(p,s)

    def test_ambiguous_backlog_source_identity_rejected(self):
        p,s=fixtures();s['tasks'].append({'id':'TASK-9','title':'Duplicate',
             'references':['docs/ROADMAP.md#R0.W1']})
        with self.assertRaises(ValueError):module.project(p,s)

    def test_unknown_dependency_rejected(self):
        p,s=fixtures();p['tasks'][1]['dependsOn']=['R9.W99']
        with self.assertRaises(ValueError):module.project(p,s)

    def test_dependency_cycle_rejected(self):
        p,s=fixtures();p['tasks'][0]['dependsOn']=['R1.W2']
        with self.assertRaises(ValueError):module.project(p,s)

    def test_path_traversal_rejected(self):
        p,s=fixtures();p['tasks'][1]['sourceRef']='../other.md#R1.W1'
        with self.assertRaises(ValueError):module.project(p,s)

    def test_unknown_priority_factors_rejected(self):
        p,s=fixtures();p['tasks'][1]['priorityFactors']['impact']='urgent!!!'
        with self.assertRaises(ValueError):module.project(p,s)

    def test_no_acceptance_criteria_rejected(self):
        p,s=fixtures();p['tasks'][1]['acceptanceCriteria']=[]
        with self.assertRaises(ValueError):module.project(p,s)

    def test_document_verified_not_equivalent_to_new_work(self):
        p,s=fixtures();p['tasks'][1]['state']='verified'
        r=module.project(p,s)
        self.assertEqual(next(x for x in r['actions'] if x['key']=='R1.W1')['disposition'],'PRESERVE_HISTORICAL')

    def test_unrecognized_cli_reference_shape_fails_closed(self):
        p,s=fixtures();s['tasks'][0]['references']=[{'id':'docs/ROADMAP.md#R0.W1'}]
        with self.assertRaises(ValueError):module.project(p,s)

    def test_reprioritization_does_not_override_backlog_settings(self):
        p,s=fixtures();r=module.project(p,s)
        x=next(x for x in r['actions'] if x['key']=='R1.W1')
        self.assertIn(x['priorityProposal']['tier'],{'P0','P1','P2','P3'})
        self.assertNotIn('cliCommand',x)

    def test_empty_packet_does_not_invent_tasks(self):
        p,s=fixtures();p['tasks']=[]
        with self.assertRaises(ValueError):module.project(p,s)

    def test_latest_milestone_ref_does_not_become_a_task(self):
        p,s=fixtures();r=module.project(p,s)
        self.assertEqual(len(r['actions']),3)
        self.assertEqual(len(r['milestones']),2)


if __name__=='__main__':unittest.main()
