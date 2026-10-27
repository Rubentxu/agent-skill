"""Behavioral router tests: problem > syntax, abstention, progressive disclosure."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fp_refactor_router', ROOT/'scripts/affordances.py')
router = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = router
spec.loader.exec_module(router)


def scenario(problem='mixed-rules-effects', facts=None, constraints=None, evidence=True,
             phase='plan', signals=None, available_skills=None, language='rust'):
    return {
        'intent': 'refactor', 'basis': 'observed', 'language': language,
        'phase': phase, 'signals': signals or ['side-effects'],
        'problems': [{'id': problem, 'evidence':
                      [{'source': 'src/usecase.rs:decision', 'observation': 'decision calls DB during validation'}]
                      if evidence else []}],
        'facts': facts or [], 'constraints': constraints or [],
        'available_skills': available_skills or [],
    }


class DecisionTests(unittest.TestCase):
    def test_confirmed_problem_and_preconditions_choose_minimal_recipe(self):
        result = router.affordances(scenario(facts=['behavior-characterized','effect-order-understood']))
        self.assertEqual(result['recommendation']['id'], 'extract-pure-decision')
        self.assertEqual(result['recommendation']['decision'], 'APPLY')
        self.assertIn('read-recipe', [x['rel'] for x in result['_links']])
        self.assertEqual(result['diagnoses'][0]['status'], 'OBSERVED')

    def test_signal_only_must_not_apply_any_recipe(self):
        state = scenario()
        state.pop('problems')
        state['facts'] = ['behavior-characterized','effect-order-understood']
        result = router.affordances(state)
        self.assertTrue(result['diagnoses'])
        self.assertTrue(all(x['status']=='INFERRED' for x in result['diagnoses']))
        self.assertFalse(any(x['decision']=='APPLY' for x in result['alternatives']))

    def test_no_evidence_is_inferred_not_observed(self):
        state = scenario(evidence=False, facts=['behavior-characterized','effect-order-understood'])
        result = router.affordances(state)
        self.assertEqual(result['diagnoses'][0]['status'], 'INFERRED')
        self.assertEqual(result['recommendation']['decision'], 'INSPECT_MORE')

    def test_missing_preconditions_requires_inspection(self):
        result = router.affordances(scenario())
        self.assertEqual(result['recommendation']['decision'], 'INSPECT_MORE')
        self.assertIn('inspect-problem', [x['rel'] for x in result['_links']])
        self.assertNotIn('read-recipe', [x['rel'] for x in result['_links']])

    def test_transaction_semantics_block_extraction(self):
        result = router.affordances(scenario(facts=['behavior-characterized','effect-order-understood'],
                                             constraints=['transaction-semantics-unknown']))
        decision = next(x for x in result['alternatives'] if x['id']=='extract-pure-decision')
        self.assertEqual(decision['decision'],'BLOCKED')

    def test_cohesive_code_needs_no_refactor_even_when_prerequisites_met(self):
        result = router.affordances(scenario(facts=['behavior-characterized','effect-order-understood'],
                                             constraints=['already-cohesive-boundary']))
        self.assertEqual(result['recommendation']['decision'],'KEEP_AS_IS')
        self.assertNotIn('read-recipe', [x['rel'] for x in result['_links']])

    def test_explicit_permission_missing_never_recommends_application(self):
        result = router.affordances(scenario(facts=['behavior-characterized','effect-order-understood'],
                                             constraints=['no-refactor-authorized']))
        self.assertEqual(result['recommendation']['decision'],'KEEP_AS_IS')

    def test_dynamic_problem_override_same_signals(self):
        facts=['behavior-characterized','effect-order-understood']
        one=router.affordances(scenario(facts=facts, problem='mixed-rules-effects'))
        two=router.affordances(scenario(facts=['consumer-path-observed'],
                                       problem='uncharacterized-legacy-code'))
        self.assertNotEqual(one['recommendation']['id'], two['recommendation']['id'])
        self.assertEqual(two['recommendation']['id'], 'legacy-seam')

    def test_unknown_wire_contract_blocks_domain_state_refactor(self):
        res=router.affordances(scenario(problem='illegal-domain-states', language='kotlin',
                   signals=['invalid-state'], facts=['domain-invariant-observed','serialization-boundary-reviewed'],
                   constraints=['unresolved-wire-contract']))
        self.assertEqual(next(x for x in res['alternatives'] if x['id']=='domain-state-refactor')['decision'],'BLOCKED')

    def test_progressive_phase_only_unveils_recipe_when_planning(self):
        state=scenario(facts=['behavior-characterized','effect-order-understood'],phase='diagnose')
        diagnosis=router.affordances(state)
        self.assertNotIn('read-recipe', [x['rel'] for x in diagnosis['_links']])
        self.assertFalse(any(x['kind']=='language' for x in diagnosis['lenses']))
        state['phase']='plan'
        plan=router.affordances(state)
        self.assertIn('read-recipe', [x['rel'] for x in plan['_links']])
        self.assertTrue(any(x['kind']=='language' for x in plan['lenses']))
        state['phase']='verify'
        verify=router.affordances(state)
        self.assertIn('verify-contracts', [x['rel'] for x in verify['_links']])
        self.assertNotIn('read-recipe', [x['rel'] for x in verify['_links']])

    def test_available_skill_is_required_for_delegation(self):
        state=scenario()
        state['signals']=['side-effects']
        self.assertNotIn('delegate-skill', [x['rel'] for x in router.affordances(state)['_links']])
        state['available_skills']=['delivery-first-testing']
        result=router.affordances(state)
        self.assertEqual([x['skill_id'] for x in result['_links'] if x['rel']=='delegate-skill'],
                         ['delivery-first-testing'])

    def test_unobserved_skill_never_executed(self):
        state=scenario()
        state['available_skills']=['another-skill']
        result=router.affordances(state)
        self.assertFalse([x for x in result['_links'] if x['rel']=='delegate-skill'])

    def test_prior_revision_prevents_decision(self):
        state=scenario(facts=['behavior-characterized','effect-order-understood'])
        state['basis']='stale'
        result=router.affordances(state)
        self.assertEqual(result['alternatives'], [])
        self.assertEqual(result['_links'][0]['rel'], 'refresh-basis')

    def test_planned_technique_not_activated(self):
        res=router.affordances(scenario())
        self.assertNotIn('distributed-effects', [r['id'] for r in res['alternatives']])

    def test_bad_evidence_rejected(self):
        s=scenario()
        s['problems'][0]['evidence']=[{'source':'source only'}]
        with self.assertRaises(ValueError): router.affordances(s)

    def test_bad_constraint_rejected(self):
        with self.assertRaises(ValueError):router.affordances(scenario(constraints=['anything']))

    def test_no_unjustified_syntactic_fold(self):
        result=router.affordances(scenario(problem='algorithm-cost-or-clarity',
              signals=['complex-algorithm'],facts=['behavior-characterized','complexity-baseline-observed'],
              constraints=['already-cohesive-boundary']))
        self.assertEqual(result['recommendation']['decision'], 'KEEP_AS_IS')

    def test_all_ready_recipe_playbooks_exist(self):
        recipes=json.loads((ROOT/'references/recipe-registry.json').read_text())['recipes']
        for recipe in recipes:
            if recipe['status'] == 'ready':
                full=(ROOT/recipe['playbook']).resolve()
                self.assertTrue(full.is_file())
                self.assertTrue(full.is_relative_to(ROOT.resolve()))

    def test_every_recipe_references_real_problem(self):
        recipes=json.loads((ROOT/'references/recipe-registry.json').read_text())['recipes']
        problems={x['id'] for x in json.loads((ROOT/'references/problems.json').read_text())['problems']}
        for recipe in recipes:self.assertTrue(set(recipe['problems']) <= problems)

    def test_no_shared_state_between_conversations(self):
        state=scenario(facts=['behavior-characterized','effect-order-understood'])
        before=router.affordances(state)
        router.affordances(scenario(constraints=['no-refactor-authorized']))
        self.assertEqual(router.affordances(state), before)

if __name__=='__main__':unittest.main()
