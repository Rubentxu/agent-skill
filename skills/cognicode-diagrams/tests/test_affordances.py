import importlib.util
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

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
        'evidence_origin': 'cognicode', 'claim_coverage': 'verified',
        'research': {"catalog":"observed","language_registry":{"source":"cognicode","version":"synthetic-1","support":"supported"},"session":{"id":"mcp-1","transport":"mcp","graph_state":"absent","graph_owner":None,"graph_basis":None,"persistence":"absent"},"view":{"node_count":2,"max_nodes":15},"question":{"id":"RQ-1","text":"Cuál es la responsabilidad implementada?","kind":"responsibilities","language":"rust","target":"module::run"},"capabilities":[{"name":"query_symbol_index","role":"symbol_index","languages":["rust"],"advertised":True,"schema_observed":True,"requires_graph":False,"requires_persistence":False,"stability":"stable","probes":{"rust":{"status":"usable","query_id":"P-1","symbol_id":"module::run","location":"src/main.rs:12","context":"present","relations":"unknown","coverage":"partial"}}}],"queries":[{"id":"Q-1","question_id":"RQ-1","target":"module::run","capability":"query_symbol_index","mode":"structured","status":"ok","coverage":"partial","observation_plane":"static","symbol_ids":["module::run"],"relation_ids":[]}],"claims":[{"id":"C-1","question_id":"RQ-1","kind":"entity","status":"observed","plane":"static","symbol_id":"module::run","query_ids":["Q-1"]}],"diagram_claim_ids":["C-1"],"scope":{"source":"cognicode","report_id":"COV-1","languages":["rust"],"coverage":"complete","omissions_complete":True,"omitted_files":[]}},
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


class StrictInvestigationTests(unittest.TestCase):
    def test_detail_request_forces_query(self):
        x = fixture(model="reviewed", detail_requested=True)
        self.assertEqual(rels(x), ["query-cognicode"])
        self.assertNotIn("render-mermaid", rels(x))

    def test_evidence_insufficient_never_renders(self):
        x = fixture(model="reviewed", evidence_insufficient=True)
        self.assertEqual(rels(x), ["query-cognicode"])
        self.assertNotEqual(engine.affordances(x)["status"], "VERIFIED")

    def test_non_cognicode_evidence_refused(self):
        x = fixture(model="reviewed", evidence_origin="other")
        self.assertEqual(rels(x), ["query-cognicode"])
        self.assertIn("ajena a CogniCode", str(engine.affordances(x)["blockers"]))

    def test_cognicode_missing_no_substitute(self):
        x = fixture(model="reviewed", environment="missing", detail_requested=True)
        self.assertEqual(engine.affordances(x)["status"], "BLOCKED")
        self.assertNotIn("query-cognicode", rels(x))

    def test_claim_coverage_unknown_not_verified(self):
        x = fixture(model="reviewed", claim_coverage="unknown",
                    artifacts={"mermaid":"valid", "structurizr":"valid"})
        self.assertNotEqual(engine.affordances(x)["status"], "VERIFIED")


class RoutingTests(unittest.TestCase):
    def test_no_question_no_architectural_model(self):
        x = fixture(model="reviewed", research=None)
        result = engine.affordances(x)
        self.assertEqual(result["recommended"], "formulate-question")
        self.assertNotIn("render-mermaid", rels(x))

    def test_grounded_question_can_render(self):
        x = fixture(model="reviewed", artifacts={"mermaid":"valid", "structurizr":"valid"})
        self.assertEqual(engine.affordances(x)["status"], "VERIFIED")

    def test_omitted_essential_file_blocks_even_with_grounded_claim(self):
        import copy
        s = fixture(model="reviewed")
        s["research"] = copy.deepcopy(s["research"])
        s["research"]["scope"].update(coverage="partial", omitted_files=[
            {"path":"src/entrypoint.rs", "relevance":"relevant", "review_query_ids":[]}])
        result = engine.affordances(s)
        self.assertEqual(result["status"], "PARTIAL")
        self.assertNotIn("render-mermaid", rels(s))

    def test_partial_scope_never_claims_global_verified(self):
        import copy
        s = fixture(model="reviewed", artifacts={"mermaid":"valid", "structurizr":"valid"})
        s["research"] = copy.deepcopy(s["research"])
        s["research"]["queries"][0]["coverage_paths"] = ["src/unused.rs"]
        s["research"]["scope"].update(coverage="partial", omitted_files=[
            {"path":"src/unused.rs", "relevance":"irrelevant", "review_query_ids":["Q-1"]}])
        self.assertNotEqual(engine.affordances(s)["status"], "VERIFIED")

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
        self.assertIn('discover-model', rels(fixture(evidence='symbols_ready')))

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


class InteractiveProjectorRoutingTests(unittest.TestCase):
    def test_likec4_is_a_format_not_a_new_lens(self):
        catalog = engine.read_catalog()
        self.assertEqual(catalog['c4']['formats']['likec4']['support'], 'adapted')
        self.assertTrue((SKILL/catalog['c4']['formats']['likec4']['playbook']).is_file())

    def test_likec4_format_is_agent_generated_from_c4_lens(self):
        x=fixture(formats=['likec4'],model='reviewed',artifacts={'likec4':'absent'}, validators={'likec4':'available'})
        self.assertIn('render-likec4',rels(x))

    def test_likec4_not_routed_into_kroki(self):
        x=fixture(intent='preview',formats=['likec4'],artifacts={'likec4':'valid'},projector='kroki-local')
        self.assertEqual(engine.affordances(x)['status'],'UNSUPPORTED')

    def test_interactive_viewer_no_cognicode_rescan(self):
        x=fixture(intent='preview',formats=['likec4'],artifacts={'likec4':'valid'},
                  environment='missing',evidence='absent',model='absent',basis='unknown',
                  projector='likec4-local',projector_status='ready')
        self.assertEqual(rels(x),['open-projector'])
        self.assertNotIn('scan-symbols',rels(x))

    def test_viewer_has_to_be_observed(self):
        x=fixture(intent='preview',formats=['structurizr'],artifacts={'structurizr':'valid'},
                  projector='structurizr-local', projector_status='unknown')
        self.assertEqual(rels(x),['inspect-projector'])

    def test_viewer_not_started_without_consent(self):
        x=fixture(intent='preview',formats=['likec4'],artifacts={'likec4':'draft'},
                  projector='likec4-local',projector_status='missing')
        self.assertEqual(engine.affordances(x)['status'],'BLOCKED')
        self.assertNotIn('start-projector',rels(x))

    def test_viewer_can_start_when_explicitly_authorized(self):
        x=fixture(intent='preview',formats=['structurizr'],artifacts={'structurizr':'draft'},
                  projector='structurizr-local',projector_status='missing',approval={'start_projector':True})
        self.assertEqual(rels(x),['start-projector'])
        self.assertTrue(engine.affordances(x)['_links'][0]['requires_approval'])

    def test_projector_must_match_format(self):
        x=fixture(intent='preview',formats=['mermaid'],artifacts={'mermaid':'valid'},
                  projector='structurizr-local',projector_status='ready')
        self.assertEqual(engine.affordances(x)['status'],'UNSUPPORTED')

    def test_viewer_http_ready_does_not_claim_vision(self):
        x=fixture(intent='preview',formats=['likec4'],artifacts={'likec4':'valid'},
                  projector='likec4-local',projector_status='ready',visual_review='not_run')
        self.assertNotEqual(engine.affordances(x)['status'],'VERIFIED')
        self.assertEqual(rels(x),['open-projector'])

    def test_interactive_visual_review_passes_but_validation_missing(self):
        x=fixture(intent='preview',formats=['likec4'],artifacts={'likec4':'draft'},
                  projector='likec4-local',projector_status='ready',visual_review='passed')
        self.assertEqual(engine.affordances(x)['status'],'PARTIAL')

    def test_interactive_verified_is_only_visual_format(self):
        x=fixture(intent='preview',formats=['structurizr'],artifacts={'structurizr':'valid'},
                  projector='structurizr-local',projector_status='ready',visual_review='passed')
        self.assertEqual(engine.affordances(x)['status'],'VERIFIED')

    def test_failed_visual_review_requires_revision(self):
        x=fixture(intent='preview',formats=['structurizr'],artifacts={'structurizr':'valid'},
                  projector='structurizr-local',projector_status='ready',visual_review='failed')
        self.assertEqual(engine.affordances(x)['status'],'PARTIAL')
        self.assertEqual(rels(x),['review-layout'])

    def test_absent_input_blocks_viewer(self):
        x=fixture(intent='preview',formats=['likec4'],artifacts={'likec4':'absent'},
                  projector='likec4-local',projector_status='ready')
        self.assertEqual(engine.affordances(x)['status'],'BLOCKED')

    def test_viewer_invalid_state_fail_closed(self):
        x=fixture(intent='preview',formats=['likec4'],artifacts={'likec4':'valid'},
                  projector='likec4-local',projector_status='cloud_ready')
        with self.assertRaises(engine.InvalidState):engine.affordances(x)
