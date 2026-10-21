import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts'/'affordances.py'
spec=importlib.util.spec_from_file_location('delivery_router',SCRIPT)
router=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=router
spec.loader.exec_module(router)


def s(**kw):
    v=dict(intent='feature',inventory='ready',impact='known',basis='current',changed=['ui'],risk='routine',affected='passed',uat='passed',regression='pending')
    v.update(kw)
    return v


def next_action(**kw):
    return router.affordances(s(**kw))['recommended']


class RegistryTests(unittest.TestCase):
    def test_valid_registry(self):
        cat=router.read_catalog()
        self.assertGreaterEqual(sum(l['status']=='ready' for l in cat.values()),7)
        self.assertIn('cross-repo-consumer',cat)
    def test_planned_not_active(self):
        self.assertEqual(router.read_catalog()['mutation-guidance']['status'],'ready')
        self.assertNotIn('mutation-guidance',[l['id'] for l in router.affordances(s())['lenses']])
    def test_no_link_escapes_skill(self):
        for p in router.ACTIONS.values():
            dest=(ROOT/p).resolve()
            self.assertTrue(dest.is_relative_to(ROOT.resolve()) and dest.is_file(),p)
    def test_duplicate_rejected(self):
        data=json.loads(router.CATALOG.read_text())
        data['lenses'].append(data['lenses'][0])
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'catalog.json';p.write_text(json.dumps(data))
            with self.assertRaises(router.InvalidState): router.read_catalog(p)
    def test_unknown_lens_state_never_added(self):
        self.assertNotIn('fake',[l['id'] for l in router.affordances(s())['lenses']])


class FeatureTests(unittest.TestCase):
    def test_catalog_is_read_only(self):
        v=router.affordances({'intent':'catalog'})
        self.assertEqual(v['recommended'],'list-lenses')
        self.assertEqual(v['status'],'READY')
    def test_unknown_inventory(self): self.assertEqual(next_action(inventory='unknown'),'inspect-project')
    def test_stale_baseline(self): self.assertEqual(next_action(basis='stale'),'refresh-basis')
    def test_unknown_impact(self): self.assertEqual(next_action(impact='unknown'),'resolve-impact')
    def test_narrow_tests_first(self): self.assertEqual(next_action(affected='not_run'),'run-affected')
    def test_real_test_failure_never_green(self):
        v=router.affordances(s(affected='failed'))
        self.assertEqual((v['recommended'],v['status']),('classify-failure','FAILED'))
    def test_blocked_is_not_pass(self): self.assertEqual(router.affordances(s(affected='blocked'))['status'],'BLOCKED')
    def test_ephemeral_acceptance(self): self.assertEqual(next_action(uat='pending'),'explore-uat')
    def test_failed_uat(self): self.assertEqual(next_action(uat='failed'),'classify-failure')
    def test_regression_promotion_only_after_pass(self): self.assertEqual(next_action(),'decide-regression')
    def test_reason_needed_if_no_uat(self):
        with self.assertRaises(router.InvalidState): router.affordances(s(uat='not_needed'))
    def test_reason_needed_if_promotion_decided(self):
        with self.assertRaises(router.InvalidState): router.affordances(s(regression='decided'))
    def test_no_need_uat_with_reason(self):
        self.assertEqual(next_action(uat='not_needed',uat_reason='pure refactor, covered by contracts'),'decide-regression')
    def test_critical_requires_acceptance(self):
        self.assertEqual(next_action(risk='critical',changed=['security'],uat='not_needed',uat_reason='tests only'),'explore-uat')
    def test_final_requires_all_decisions(self):
        v=router.affordances(s(regression='decided',regression_reason='existing contract protects it'))
        self.assertEqual((v['recommended'],v['status']),('finish-feature','DONE'))
    def test_invalid_signal_fails_closed(self):
        with self.assertRaises(router.InvalidState): router.affordances(s(changed=['imaginary']))


class StageTests(unittest.TestCase):
    def test_merge_minimal(self):
        v=router.affordances(s(intent='merge',merge_checks='not_run'))
        self.assertEqual(v['recommended'],'run-merge')
    def test_merge_done(self):
        self.assertEqual(next_action(intent='merge',merge_checks='passed'),'finish-merge')
    def test_merge_red(self): self.assertEqual(next_action(intent='merge',merge_checks='failed'),'classify-failure')
    def test_integration_run(self): self.assertEqual(next_action(intent='integration'),'run-integration')
    def test_integration_done(self): self.assertEqual(next_action(intent='integration',integration_checks='passed'),'finish-integration')
    def test_integration_failure(self): self.assertEqual(router.affordances(s(intent='integration',integration_checks='failed'))['status'],'FAILED')
    def test_release_no_artifact(self): self.assertEqual(router.affordances(s(intent='release'))['status'],'BLOCKED')
    def test_release_real_artifact(self): self.assertEqual(next_action(intent='release',artifact='ready'),'run-release')
    def test_release_done(self): self.assertEqual(next_action(intent='release',artifact='ready',release_checks='passed'),'finish-release')
    def test_release_fail(self): self.assertEqual(router.affordances(s(intent='release',artifact='ready',release_checks='failed'))['status'],'FAILED')
    def test_peer_only_when_observed_available(self):
        self.assertEqual(router.affordances(s())['related_skills'],[])
        peers=router.affordances(s(intent='merge',changed=['ci'],available_skills=['pipelinek-local-ci']))['related_skills']
        self.assertEqual(peers[0]['id'],'pipelinek-local-ci')
    def test_peer_not_autoinstalled(self):
        peers=router.affordances(s(intent='merge',changed=['ci'],available_skills=['playwright-cli']))['related_skills']
        self.assertEqual(peers,[])
    def test_unknown_change_proposes_not_activates_lens(self):
        v=router.affordances(s(changed=['unknown']))
        self.assertEqual(v['discovery'][0]['rel'],'propose-lens')
        self.assertFalse(any(l['id']=='historical-test-impact' for l in v['lenses']))
    def test_explicit_lens_gap(self):
        self.assertTrue(router.affordances(s(lens_gap=True))['discovery'])
    def test_invalid_lens_gap(self):
        with self.assertRaises(router.InvalidState):router.affordances(s(lens_gap='yes'))
    def test_invalid_peer_list(self):
        with self.assertRaises(router.InvalidState):router.affordances(s(available_skills=['../../x']))
    def test_audit_no_execution(self): self.assertEqual(next_action(intent='audit'),'audit-portfolio')
    def test_no_fake_authority(self): self.assertIn('no suite executed',router.affordances(s())['notice'])


class CLITests(unittest.TestCase):
    def test_success_json(self):
        run=subprocess.run([sys.executable,str(SCRIPT),str(ROOT/'examples'/'session-feature.json')],capture_output=True,text=True,check=False)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(json.loads(run.stdout)['recommended'],'decide-regression')
    def test_invalid_input_exit_2(self):
        run=subprocess.run([sys.executable,str(SCRIPT),'-'],input='{bad',capture_output=True,text=True,check=False)
        self.assertEqual(run.returncode,2)
        self.assertIn('INVALID_STATE',run.stderr)


if __name__=='__main__':unittest.main()
