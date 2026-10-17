"""Executable decision tests; no CogniCode runtime and no repository inspection."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from research_protocol import ResearchError, decide


def probe(state="usable", **overrides):
    d = {"status": state, "query_id": "P-1", "symbol_id": "S::run",
         "location": "src/main.kt:17", "context": "present", "relations": "unknown",
         "coverage": "partial"}
    d.update(overrides)
    return d


def cap(name="index", role="symbol_index", status="usable", language="kotlin", **kw):
    d = {"name": name, "role": role, "languages": [language], "advertised": True,
         "schema_observed": True, "requires_graph": False, "requires_persistence": False,
         "stability": "stable", "probes": {language: probe(status)}}
    d.update(kw)
    return d


def query(name="index", mode="structured", **kw):
    d = {"id": "Q-1", "question_id": "RQ-1", "capability": name, "target": "S::run",
         "mode": mode, "status": "ok", "coverage": "partial",
         "observation_plane": "static", "symbol_ids": ["S::run", "R::save"],
         "relation_ids": ["rel-1"]}
    d.update(kw)
    return d


def state(kind="responsibilities", caps=None, queries=None, claims=None, diagram=None, **kw):
    s = {
        "catalog": "observed",
        "language_registry": {"source": "cognicode", "version": "synthetic-1", "language": "kotlin",
                              "support": "supported"},
        "session": {"id": "mcp-1", "transport": "mcp", "graph_state": "absent",
                    "graph_owner": None, "graph_basis": None, "persistence": "absent"},
        "view": {"node_count": 2, "max_nodes": 15},
        "question": {"id": "RQ-1", "text": "What does this implementation do?",
                     "kind": kind, "language": "kotlin", "target": "S::run"},
        "capabilities": [cap()] if caps is None else caps,
        "queries": [] if queries is None else queries,
        "claims": [] if claims is None else claims,
        "diagram_claim_ids": [] if diagram is None else diagram,
        "max_queries": 4,
        "scope": {"source": "cognicode", "report_id": "COV-1",
                  "languages": ["kotlin"], "coverage": "complete",
                  "omissions_complete": True, "omitted_files": []},
    }
    s.update(kw)
    return s


def entity(**kw):
    d = {"id": "C-1", "question_id": "RQ-1", "kind": "entity", "status": "observed",
         "plane": "static", "symbol_id": "S::run", "query_ids": ["Q-1"]}
    d.update(kw)
    return d


def relation(**kw):
    d = {"id": "R-1", "question_id": "RQ-1", "kind": "relation", "status": "observed",
         "plane": "static", "from_symbol": "S::run", "to_symbol": "R::save",
         "relation_id": "rel-1", "query_ids": ["Q-1"]}
    d.update(kw)
    return d


class QuestionProtocolTests(unittest.TestCase):
    def test_no_question_needs_formulation(self):
        self.assertEqual(decide(None)["action"], "formulate-question")

    def test_unobserved_catalog_needs_discovery(self):
        self.assertEqual(decide(state(catalog="unknown"))["action"], "discover-capabilities")

    def test_advertised_only_never_assumes_usable(self):
        s = state(caps=[cap(schema_observed=False)])
        self.assertEqual(decide(s)["status"], "PARTIAL")

    def test_probe_on_real_symbol_before_using_tool(self):
        s = state(caps=[cap(status="untried")])
        d = decide(s)
        self.assertEqual((d["action"], d["capability"]), ("probe-capability", "index"))

    def test_verified_index_candidate_is_preferred(self):
        s = state(caps=[cap(name="index", role="symbol_index"), cap(name="intent", role="intent_search")])
        self.assertEqual(decide(s)["capability"], "index")
        self.assertEqual(decide(s)["action"], "query-structured")

    def test_failing_graph_does_not_mean_kotlin_unsupported(self):
        s = state("interaction", caps=[
            cap("graph", "subgraph", "failed"),
            cap("path", "trace_path", "usable"),
        ])
        self.assertEqual(decide(s)["capability"], "path")
        self.assertEqual(decide(s)["action"], "query-structured")

    def test_no_language_wide_failure_claim(self):
        s = state("interaction", caps=[cap("graph", "subgraph", "failed")])
        d = decide(s)
        self.assertEqual(d["status"], "PARTIAL")
        self.assertIn("pregunta", d["why"])
        self.assertNotIn("incompatible", d["why"].split("no declarar")[0])

    def test_raw_read_file_cannot_be_used_as_structural_proof(self):
        s = state(caps=[cap("read_file", "symbol_index")],
                  queries=[query("read_file", mode="raw")],
                  claims=[entity()], diagram=["C-1"])
        d = decide(s)
        self.assertEqual(d["status"], "BLOCKED")
        self.assertIsNone(d["action"])

    def test_file_wrappers_and_mutating_tools_cannot_launder_code_reads(self):
        for tool in ("list_files", "write_file", "edit_file", "resources/read"):
            with self.subTest(tool=tool):
                s = state(caps=[cap(tool, "symbol_index")],
                          queries=[query(tool)],
                          claims=[entity()], diagram=["C-1"])
                self.assertEqual(decide(s)["status"], "BLOCKED")
        s = state(caps=[cap("refactor_apply", "symbol_index", authority="mutating")],
                  queries=[query("refactor_apply")],
                  claims=[entity()], diagram=["C-1"])
        self.assertEqual(decide(s)["status"], "BLOCKED")

    def test_file_reader_never_suggested_for_probe_or_query(self):
        s = state(caps=[cap("list_files", "symbol_index")])
        result = decide(s)
        self.assertEqual(result["status"], "PARTIAL")
        self.assertIsNone(result["capability"])
        self.assertIsNone(result["action"])

    def test_mutating_capability_is_skipped_before_probe(self):
        s = state(caps=[cap("unsafe_apply", "symbol_index", authority="mutating"),
                        cap("safe_index", "symbol_index")])
        d = decide(s)
        self.assertEqual(d["capability"], "safe_index")
        self.assertEqual(d["action"], "query-structured")

    def test_new_semantic_questions_choose_discovered_cognicode_roles(self):
        for kind, role in (
            ("change_impact", "impact_analysis"),
            ("dependency_structure", "communities"),
            ("traceable_decomposition", "symbol_context")
        ):
            with self.subTest(kind=kind):
                s = state(kind, caps=[cap("observed_runtime_tool", role)])
                d = decide(s)
                self.assertEqual(d["action"], "query-structured")
                self.assertEqual(d["capability"], "observed_runtime_tool")

    def test_search_content_may_locate_only_candidates(self):
        s = state(caps=[cap("search_content", "symbol_index"), cap("index", "symbol_index")],
                  queries=[query("search_content", mode="text_candidate")],
                  claims=[entity()], diagram=["C-1"])
        d = decide(s)
        self.assertEqual(d["action"], "justify-claims")  # proposed claim is not established
        s["claims"] = []
        s["diagram_claim_ids"] = []
        self.assertEqual(decide(s)["capability"], "index")

    def test_text_candidate_without_structured_capability_partial(self):
        s = state(caps=[cap("search_content", "symbol_index")],
                  queries=[query("search_content", mode="text_candidate")])
        self.assertEqual(decide(s)["status"], "PARTIAL")

    def test_structured_entity_reuses_existing_query_without_extra_calls(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"])
        d = decide(s)
        self.assertEqual(d["status"], "EVIDENCE_READY")
        self.assertIsNone(d["action"])

    def test_relation_requires_the_edge_and_both_endpoints(self):
        s = state("collaborators", caps=[cap("refs", "references")],
                  queries=[query("refs", relation_ids=[])],
                  claims=[relation()], diagram=["R-1"])
        self.assertEqual(decide(s)["action"], "justify-claims")

    def test_relation_with_edge_is_grounded(self):
        s = state("collaborators", caps=[cap("refs", "references")],
                  queries=[query("refs")], claims=[relation()], diagram=["R-1"])
        self.assertEqual(decide(s)["status"], "EVIDENCE_READY")

    def test_runtime_not_proven_by_static_graph(self):
        s = state("collaborators", caps=[cap("refs", "references")],
                  queries=[query("refs")], claims=[relation(plane="runtime")],
                  diagram=["R-1"])
        self.assertNotEqual(decide(s)["status"], "EVIDENCE_READY")

    def test_unobserved_inference_not_renderable_as_implemented(self):
        s = state(queries=[query()], claims=[entity(status="inferred")], diagram=["C-1"])
        self.assertEqual(decide(s)["action"], "justify-claims")

    def test_bounded_queries_stop_without_loop(self):
        s = state(queries=[query(status="failed")], max_queries=1)
        d = decide(s)
        self.assertEqual(d["status"], "PARTIAL")
        self.assertIsNone(d["action"])

    def test_same_tool_same_target_is_not_repeated(self):
        s = state(queries=[query(status="partial", symbol_ids=[])])
        self.assertEqual(decide(s)["status"], "PARTIAL")

    def test_mismatched_question_id_rejected(self):
        s = state(queries=[query(question_id="ANOTHER")])
        with self.assertRaises(ResearchError):
            decide(s)

    def test_duplicate_query_ids_rejected(self):
        s = state(queries=[query(), query()])
        with self.assertRaises(ResearchError):
            decide(s)

    def test_missing_provenance_fields_fail_closed(self):
        s = state(caps=[cap(probes={"kotlin": {"status": "usable"}})])
        with self.assertRaises(ResearchError):
            decide(s)

    def test_unprobed_structured_tool_cannot_certify(self):
        s = state(caps=[cap(status="untried")], queries=[query()],
                  claims=[entity()], diagram=["C-1"])
        self.assertEqual(decide(s)["status"], "BLOCKED")

    def test_wrong_language_cannot_certify(self):
        s = state(caps=[cap(language="rust")], queries=[query()],
                  claims=[entity()], diagram=["C-1"])
        self.assertEqual(decide(s)["status"], "BLOCKED")

    def test_advertised_without_schema_cannot_certify(self):
        s = state(caps=[cap(schema_observed=False)], queries=[query()],
                  claims=[entity()], diagram=["C-1"])
        self.assertEqual(decide(s)["status"], "BLOCKED")



    def test_missing_coverage_report_requires_cognicode_check(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"])
        del s["scope"]
        self.assertEqual(decide(s)["action"], "assess-coverage")

    def test_missing_omissions_inventory_never_accepts_partial_graph(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"])
        s["scope"].update(coverage="partial", omissions_complete=False)
        self.assertEqual(decide(s)["action"], "assess-coverage")

    def test_omission_unknown_triggers_targeted_structured_research(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"])
        s["scope"].update(
            coverage="partial",
            omitted_files=[{"path":"src/workers/runner.kt", "relevance":"unknown",
                            "review_query_ids": []}])
        verdict = decide(s)
        self.assertEqual(verdict["action"], "assess-omissions")
        self.assertIn("src/workers/runner.kt", verdict["missing"])

    def test_relevant_omission_blocks_even_when_all_claims_have_symbols(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"])
        s["scope"].update(
            coverage="partial",
            omitted_files=[{"path":"src/workers/runner.kt", "relevance":"relevant",
                            "review_query_ids":["Q-1"]}])
        verdict = decide(s)
        self.assertEqual(verdict["status"], "PARTIAL")
        self.assertIsNone(verdict["action"])

    def test_omission_marked_irrelevant_without_structured_evidence_is_not_accepted(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"])
        s["scope"].update(
            coverage="partial",
            omitted_files=[{"path":"src/unused.kt", "relevance":"irrelevant",
                            "review_query_ids":["Q-1"]}])
        self.assertEqual(decide(s)["status"], "PARTIAL")

    def test_structured_review_can_mark_omitted_file_irrelevant_only_with_path(self):
        s = state(queries=[query(coverage_paths=["src/unused.kt"])],
                  claims=[entity()], diagram=["C-1"])
        s["scope"].update(
            coverage="partial",
            omitted_files=[{"path":"src/unused.kt", "relevance":"irrelevant",
                            "review_query_ids":["Q-1"]}])
        verdict = decide(s)
        self.assertEqual(verdict["status"], "EVIDENCE_READY")
        self.assertIn("parcial", verdict["why"])

    def test_rust_probe_never_certifies_kotlin_from_same_catalog_capability(self):
        s = state(caps=[cap(probes={"rust": probe("usable")}, languages=["rust", "kotlin"])])
        self.assertEqual(decide(s)["action"], "probe-capability")

    def test_rust_probe_does_not_authorize_kotlin_query(self):
        s = state(caps=[cap(probes={"rust": probe("usable")}, languages=["rust", "kotlin"])],
                  queries=[query()], claims=[entity()], diagram=["C-1"])
        self.assertEqual(decide(s)["status"], "BLOCKED")

    def test_project_language_outside_observed_scope_cannot_certify(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"])
        s["scope"]["languages"] = ["rust"]
        self.assertEqual(decide(s)["status"], "PARTIAL")

    def test_contradictory_complete_and_skipped_files_rejected(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"])
        s["scope"]["omitted_files"] = [{"path":"src/fail.kt", "relevance":"unknown",
                                        "review_query_ids":[]}]
        with self.assertRaises(ResearchError):
            decide(s)

    def test_no_infinite_retry_after_structured_coverage_check(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"])
        s["scope"].update(coverage="unknown", omissions_complete=False,
                          review_query_ids=["Q-1"])
        verdict = decide(s)
        self.assertEqual(verdict["status"], "PARTIAL")
        self.assertIsNone(verdict["action"])

    def test_runtime_language_preflight_before_global_c4(self):
        s = state(language_registry={"source": "cognicode", "version": "v0.101.17",
                                     "language": "kotlin", "support": "not_listed"})
        self.assertEqual(decide(s)["status"], "PARTIAL")
        self.assertIn("C4 global", decide(s)["why"])

    def test_missing_preflight_requests_installed_registry(self):
        s = state()
        del s["language_registry"]
        self.assertEqual(decide(s)["action"], "preflight-language")

    def test_missing_session_requests_current_process(self):
        s = state()
        del s["session"]
        self.assertEqual(decide(s)["action"], "inspect-session")

    def test_graph_only_tool_requires_same_process_build(self):
        s = state("interaction", caps=[cap("graph", "subgraph", requires_graph=True)])
        self.assertEqual(decide(s)["action"], "build-graph")
        s["session"].update(graph_state="current", graph_owner="different-process",
                            graph_basis="digest1")
        self.assertEqual(decide(s)["action"], "build-graph")
        s["session"]["graph_owner"] = "mcp-1"
        self.assertEqual(decide(s)["action"], "query-structured")

    def test_no_graph_error_is_missing_precondition_not_unsupported(self):
        s = state("interaction", caps=[cap("graph", "subgraph", "failed", requires_graph=True)],
                  queries=[query("graph", status="failed", error_code="NO_GRAPH_AVAILABLE",
                                 relation_ids=[], symbol_ids=[])])
        result = decide(s)
        self.assertEqual(result["action"], "build-graph")
        self.assertNotEqual(result["status"], "UNSUPPORTED")

    def test_after_failed_graph_build_do_not_retry_indefinitely(self):
        s = state("interaction", caps=[
            cap("graph", "subgraph", "failed", requires_graph=True),
            cap("code", "symbol_context")
        ])
        s["session"].update(graph_state="failed", graph_attempts=1)
        self.assertEqual(decide(s)["capability"], "code")
        self.assertEqual(decide(s)["action"], "query-structured")

    def test_language_preflight_is_bound_to_exact_language(self):
        s = state()
        s["language_registry"]["language"] = "rust"
        with self.assertRaises(ResearchError):
            decide(s)

    def test_catalog_metadata_missing_is_not_silently_guessed(self):
        s = state(caps=[cap()])
        del s["capabilities"][0]["requires_graph"]
        with self.assertRaises(ResearchError):
            decide(s)

    def test_reference_location_not_mislabelled_graph_edge(self):
        r = relation(relation_source="reference_link", relation_id=None,
                     reference={"query_id": "Q-1", "index": 0,
                                "path": "src/Caller.java", "line": 42})
        q = query("refs", relation_ids=[], reference_hits=[
            {"index": 0, "path": "src/Caller.java", "line": 42}])
        s = state("collaborators", caps=[cap("refs", "references")],
                  queries=[q], claims=[r], diagram=["R-1"])
        self.assertEqual(decide(s)["status"], "EVIDENCE_READY")
        s["claims"][0]["reference"]["line"] = 43
        self.assertEqual(decide(s)["action"], "justify-claims")

    def test_reference_cannot_claim_graph_relation_id(self):
        s = state("collaborators", caps=[cap("refs", "references")],
                  queries=[query("refs", reference_hits=[{"index": 1, "path": "x", "line": 9}])],
                  claims=[relation(relation_source="reference_link", relation_id="fake",
                        reference={"query_id": "Q-1", "index": 1, "path": "x", "line": 9})],
                  diagram=["R-1"])
        self.assertEqual(decide(s)["action"], "justify-claims")

    def test_reference_before_graph_on_collaboration(self):
        s = state("collaborators", caps=[
            cap("refs", "references"), cap("graph", "call_hierarchy", requires_graph=True)
        ])
        self.assertEqual(decide(s)["capability"], "refs")

    def test_large_view_requests_split_instead_of_unreadable_diagram(self):
        s = state(queries=[query()], claims=[entity()], diagram=["C-1"],
                  view={"node_count": 29, "max_nodes": 15})
        self.assertEqual(decide(s)["action"], "split-view")

    def test_unsupported_persistence_requirement_skips_to_available_tool(self):
        s = state("collaborators", caps=[
            cap("persisted", "references", requires_persistence=True),
            cap("refs", "references")
        ])
        self.assertEqual(decide(s)["capability"], "refs")


if __name__ == "__main__":
    unittest.main()
