import importlib.util
import json
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / 'scripts' / 'affordances.py'
spec = importlib.util.spec_from_file_location('diagrams_affordances', SCRIPT)
engine = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = engine
spec.loader.exec_module(engine)


def fixture(**changes):
    state = {
        'workspace': 'ready', 'intent': 'create', 'lens': 'c4', 'formats': ['mermaid','structurizr'],
        'environment': 'both_ready', 'evidence': 'graph_ready', 'basis': 'current',
        'model': 'absent', 'has_input_diagram': False, 'reconciled': False,
        'artifacts': {'mermaid':'absent','structurizr':'absent'},
        'validators': {'mermaid':'available','structurizr':'available'},
        'approval': {'install': False,'write_project': False}
    }
    state.update(changes)
    return state


def rels(s):
    return [x['rel'] for x in engine.affordances(s)['_links']]


class CatalogTests(unittest.TestCase):
    def test_only_c4_is_active_initially(self):
        cat = engine.read_catalog()
        self.assertEqual([k for k,v in cat.items() if v['status']=='ready'], ['c4'])
        self.assertIn('vertical-slice', cat)
        self.assertIn('use-case', cat)
        self.assertIn('class', cat)

    def test_catalog_browsing_requires_no_environment(self):
        result = engine.affordances({'intent':'catalog'})
        self.assertEqual(result['recommended'], 'list-lenses')
        self.assertEqual(len(result['lenses']), 4)

    def test_all_registered_playbooks_exist(self):
        for lens in engine.read_catalog().values():
            self.assertTrue((SKILL / lens['playbook']).is_file())

    def test_all_links_point_inside_bundle(self):
        for href in engine.LINKS.values():
            self.assertTrue((SKILL / href).is_file(), href)

    def test_active_c4_has_two_format_guides(self):
        desc = engine.read_catalog()['c4']
        for fmt in ('mermaid','structurizr'):
            self.assertTrue((SKILL / desc['formats'][fmt]['playbook']).is_file())

    def test_future_class_does_not_claim_dsl_support(self):
        cat = engine.read_catalog()
        self.assertEqual(cat['class']['formats']['structurizr']['support'], 'unsupported')


class RoutingTests(unittest.TestCase):
    def test_ready_graph_leads_to_discovery(self):
        self.assertEqual(rels(fixture()), ['discover-model'])

    def test_model_ready_offers_both_renderers(self):
        self.assertEqual(rels(fixture(model='reviewed')), ['render-mermaid','render-structurizr'])

    def test_missing_install_requires_approval(self):
        result = engine.affordances(fixture(environment='missing',evidence='absent'))
        self.assertEqual(result['status'],'BLOCKED')
        self.assertNotIn('install-cognicode', rels(fixture(environment='missing',evidence='absent')))

    def test_authorized_install_offered(self):
        x = fixture(environment='missing',evidence='absent', approval={'install':True})
        self.assertEqual(engine.affordances(x)['recommended'],'install-cognicode')

    def test_setup_without_lens_is_usable(self):
        x = fixture(intent='setup', lens=None, formats=[])
        self.assertEqual(engine.affordances(x)['status'], 'VERIFIED')

    def test_scan_without_lens_ends_after_symbols_by_default(self):
        x = fixture(intent='scan', lens=None, formats=[], evidence='symbols_ready')
        self.assertEqual(rels(x), ['finish'])

    def test_scan_without_lens_graph_when_explicit(self):
        x = fixture(intent='scan', lens=None, formats=[], evidence='symbols_ready', scan_depth='graph')
        self.assertEqual(rels(x), ['build-graph', 'finish'])

    def test_partial_scan_never_verified(self):
        x = fixture(intent='scan', lens=None, formats=[], evidence='partial')
        self.assertEqual(engine.affordances(x)['status'], 'PARTIAL')

    def test_cli_only_can_scan(self):
        self.assertIn('scan-symbols', rels(fixture(environment='cli_ready',evidence='absent')))

    def test_index_not_graph_requires_graph(self):
        self.assertIn('build-graph', rels(fixture(evidence='symbols_ready')))

    def test_stale_blocks_render(self):
        x = fixture(intent='update',model='reviewed', basis='stale', evidence='stale')
        self.assertIn('scan-symbols', rels(x))
        self.assertNotIn('render-mermaid', rels(x))

    def test_translate_without_cognicode(self):
        x = fixture(intent='translate',formats=['mermaid'], environment='missing',evidence='absent',basis='unknown',model='absent',has_input_diagram=True)
        self.assertEqual(rels(x), ['interpret-input'])

    def test_input_before_scanning(self):
        x = fixture(intent='update', model='absent',has_input_diagram=True,evidence='absent')
        self.assertEqual(rels(x), ['interpret-input'])

    def test_planned_lenses_must_be_refused(self):
        for ident in ('class','use-case','vertical-slice'):
            self.assertEqual(engine.affordances(fixture(lens=ident))['status'],'UNSUPPORTED')

    def test_unknown_lens_refused(self):
        self.assertEqual(engine.affordances(fixture(lens='random'))['status'],'UNSUPPORTED')

    def test_draft_artifact_without_validator_partial(self):
        x = fixture(model='reviewed',artifacts={'mermaid':'draft','structurizr':'draft'},validators={'mermaid':'missing','structurizr':'missing'})
        result=engine.affordances(x)
        self.assertEqual(result['status'],'PARTIAL')
        self.assertIn('finish',rels(x))
        self.assertNotIn('validate',rels(x))

    def test_validated_outputs_verified(self):
        x = fixture(model='reviewed',artifacts={'mermaid':'valid','structurizr':'valid'})
        self.assertEqual(engine.affordances(x)['status'],'VERIFIED')

    def test_model_draft_cannot_become_verified(self):
        x = fixture(model='draft',artifacts={'mermaid':'valid','structurizr':'valid'})
        self.assertEqual(engine.affordances(x)['recommended'],'review-model')

    def test_reconcile_before_update(self):
        x = fixture(intent='update',model='reviewed',reconciled=False)
        self.assertEqual(rels(x), ['reconcile'])

    def test_reconciled_update_can_render(self):
        x = fixture(intent='update',model='reviewed',reconciled=True)
        self.assertIn('render-mermaid',rels(x))

    def test_invalid_environment_is_rejected(self):
        with self.assertRaises(engine.InvalidState):
            engine.affordances(fixture(environment='fictitious'))

    def test_invalid_intent_is_rejected(self):
        with self.assertRaises(engine.InvalidState):
            engine.affordances(fixture(intent='destroy'))

    def test_validation_no_input_blocks(self):
        x = fixture(intent='validate',model='absent',formats=['mermaid'],has_input_diagram=False)
        self.assertEqual(engine.affordances(x)['status'],'BLOCKED')

    def test_json_example_routes(self):
        x = json.loads((SKILL/'examples/session-c4.json').read_text(encoding='utf-8'))
        self.assertEqual(engine.affordances(x)['recommended'],'discover-model')


if __name__ == '__main__':
    unittest.main()

class PreviewRoutingTests(unittest.TestCase):
    def test_preview_never_demands_cognicode_scan(self):
        x = fixture(intent='preview',environment='missing',evidence='absent',basis='unknown',model='absent',formats=['structurizr'],artifacts={'structurizr':'valid'},kroki='gateway_ready')
        self.assertEqual(rels(x),['preview-structurizr'])

    def test_gateway_only_blocks_mermaid_without_permission(self):
        x = fixture(intent='preview',kroki='gateway_ready',artifacts={'mermaid':'draft','structurizr':'valid'})
        self.assertEqual(rels(x),['preview-structurizr'])
        self.assertIn('companion',str(engine.affordances(x)['blockers']))

    def test_gateway_only_can_offer_authorized_companion(self):
        x = fixture(intent='preview',kroki='gateway_ready',artifacts={'mermaid':'draft','structurizr':'valid'},approval={'start_kroki':True})
        self.assertIn('start-mermaid-companion',rels(x))

    def test_kroki_unknown_observe_first(self):
        x = fixture(intent='preview',artifacts={'mermaid':'draft','structurizr':'draft'})
        self.assertEqual(rels(x),['inspect-kroki'])

    def test_missing_kroki_fails_closed(self):
        x = fixture(intent='preview',kroki='missing',artifacts={'mermaid':'draft','structurizr':'draft'})
        self.assertEqual(engine.affordances(x)['status'],'BLOCKED')

    def test_only_authorized_bootstrap(self):
        x = fixture(intent='preview',kroki='missing',artifacts={'mermaid':'draft','structurizr':'draft'},approval={'start_kroki':True})
        self.assertEqual(rels(x),['start-kroki'])
        self.assertTrue(engine.affordances(x)['_links'][0]['requires_approval'])

    def test_full_renderer_handles_both(self):
        x = fixture(intent='preview',kroki='full_ready',artifacts={'mermaid':'draft','structurizr':'valid'})
        self.assertEqual(rels(x),['preview-mermaid','preview-structurizr'])

    def test_preview_no_source_is_blocked(self):
        x = fixture(intent='preview',kroki='full_ready',artifacts={'mermaid':'absent','structurizr':'absent'})
        self.assertEqual(engine.affordances(x)['status'],'BLOCKED')

    def test_rendered_not_verified_if_source_not_valid(self):
        x = fixture(intent='preview',kroki='full_ready',artifacts={'mermaid':'draft','structurizr':'valid'},previews={'mermaid':'rendered','structurizr':'rendered'})
        self.assertEqual(engine.affordances(x)['status'],'PARTIAL')

    def test_all_sources_valid_and_previews_rendered(self):
        x = fixture(intent='preview',kroki='full_ready',artifacts={'mermaid':'valid','structurizr':'valid'},previews={'mermaid':'rendered','structurizr':'rendered'})
        self.assertEqual(engine.affordances(x)['status'],'VERIFIED')

    def test_unknown_render_state_fail_closed(self):
        with self.assertRaises(engine.InvalidState):
            engine.affordances(fixture(intent='preview',kroki='cloud_connected'))

    def test_unobserved_companion_never_render_mermaid(self):
        x = fixture(intent='preview',kroki='gateway_ready',formats=['mermaid'],artifacts={'mermaid':'draft'})
        self.assertNotIn('preview-mermaid',rels(x))


class WorkspaceRoutingTests(unittest.TestCase):
    def test_create_missing_workspace_is_first_action(self):
        self.assertEqual(rels(fixture(workspace="unknown")), ["inspect-workspace"])
        self.assertEqual(rels(fixture(workspace="absent")), ["init-workspace"])

    def test_preview_cannot_write_before_workspace_ready(self):
        x = fixture(intent="preview", workspace="absent", kroki="full_ready",
                    artifacts={"mermaid": "valid", "structurizr": "valid"})
        self.assertEqual(rels(x), ["init-workspace"])

    def test_scan_cannot_run_before_workspace_ready(self):
        x = fixture(intent="scan", lens=None, formats=[], workspace="unknown")
        self.assertEqual(rels(x), ["inspect-workspace"])

    def test_workspace_invalid_fails_closed(self):
        x = fixture(workspace="invalid")
        self.assertEqual(engine.affordances(x)["status"], "BLOCKED")
        self.assertEqual(rels(x), [])

    def test_workspace_incomplete_can_be_recovered(self):
        self.assertEqual(rels(fixture(workspace="incomplete")), ["init-workspace"])

    def test_no_workspace_needed_for_catalog(self):
        self.assertEqual(engine.affordances({"intent": "catalog"})["status"], "READY")

    def test_no_workspace_needed_for_environment_setup(self):
        x = fixture(intent="setup", lens=None, formats=[], workspace="unknown")
        self.assertEqual(engine.affordances(x)["status"], "VERIFIED")
