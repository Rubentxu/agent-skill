import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import atlas
import render_markmap
import workspace


def repo_setup(tmp):
    home = tmp / 'home'; home.mkdir()
    repo = tmp / 'repo'; repo.mkdir()
    subprocess.run(['git','init','-q',str(repo)], check=True, capture_output=True)
    workspace.init(repo, home=home)
    workspace.init_lens(repo, 'c4', home=home)
    w = Path(workspace.inspect(repo, home=home)['workspace'])
    s = w/'lenses'/'c4'/'sources'/'workspace.dsl'; s.write_text('workspace "sample" "sample" { model {} views {} }')
    r = w/'lenses'/'c4'/'renders'/'context.svg'; r.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    return home, repo, w, s, r


class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home, self.repo, self.w, self.s, self.r = repo_setup(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_build_navigation_markdown_links_to_real_assets(self):
        result=atlas.build(self.repo, home=self.home)
        self.assertEqual(result['status'], 'ATLAS_SOURCE_READY')
        content=Path(result['markdown']).read_text()
        self.assertIn('![context](../lenses/c4/renders/context.svg)',content)
        self.assertIn('[workspace.dsl](../lenses/c4/sources/workspace.dsl)',content)
        self.assertNotIn(str(self.repo),content)
        self.assertTrue(Path(result['markdown']).is_relative_to(self.w))
        self.assertEqual(atlas.check(self.repo, home=self.home)['status'],'CURRENT')

    def test_idempotent_and_stale_after_image_change(self):
        result=atlas.build(self.repo, home=self.home)
        m=Path(result['markdown']); old=m.stat().st_mtime_ns
        atlas.build(self.repo, home=self.home)
        self.assertEqual(m.stat().st_mtime_ns,old)
        self.r.write_text('<svg changed="true"/>')
        self.assertEqual(atlas.check(self.repo,home=self.home)['status'],'STALE')
        atlas.build(self.repo,home=self.home)
        self.assertEqual(atlas.check(self.repo,home=self.home)['status'],'CURRENT')

    def test_added_file_stale_and_rebuild(self):
        atlas.build(self.repo,home=self.home)
        (self.r.parent/'other.png').write_bytes(b'png')
        self.assertEqual(atlas.check(self.repo,home=self.home)['status'],'STALE')
        self.assertEqual(atlas.build(self.repo,home=self.home)['artifacts'],3)

    def test_bad_links_never_created(self):
        (self.r.parent/'escape.svg').symlink_to(self.repo/'.git'/'HEAD')
        with self.assertRaises(atlas.AtlasError):
            atlas.build(self.repo, home=self.home)
        self.assertFalse((self.w/'navigation'/'atlas.md').exists())

    def test_does_not_replace_user_authored_navigation(self):
        nav=self.w/'navigation';nav.mkdir()
        (nav/'atlas.md').write_text('my own notes')
        with self.assertRaises(atlas.AtlasError):
            atlas.build(self.repo,home=self.home)
        self.assertEqual((nav/'atlas.md').read_text(),'my own notes')

    def test_no_assets_failure(self):
        self.s.unlink();self.r.unlink()
        with self.assertRaises(atlas.AtlasError):
            atlas.build(self.repo,home=self.home)

    def test_no_projector_url_without_explicit_discovery(self):
        src=atlas.build(self.repo,home=self.home)['markdown']
        self.assertNotIn('127.0.0.1', Path(src).read_text())

    def test_url_only_for_verified_projector(self):
        with patch.object(atlas, 'discover_viewers', return_value={'c4':['[likec4 local](http://127.0.0.1:5173/)']}):
            result=atlas.build(self.repo,home=self.home,inspect_viewers=True)
        self.assertEqual(result['viewer_links'],1)
        self.assertIn('http://127.0.0.1:5173/',Path(result['markdown']).read_text())

    def test_garbage_filename_escaped_and_url_encoded(self):
        strange=self.r.parent/'bad(name)[x].svg'
        strange.write_text('<svg/>')
        result=atlas.build(self.repo,home=self.home)
        body=Path(result['markdown']).read_text()
        self.assertIn('bad%28name%29%5Bx%5D.svg',body)
        self.assertNotIn('bad(name)[x].svg',body)

    def test_report_is_not_cognicode_graph(self):
        r=atlas.build(self.repo,home=self.home)
        data=json.loads(Path(r['manifest']).read_text())
        self.assertEqual(data['semantic_certification'],'not_claimed')
        self.assertEqual(data['generator'],'cognicode-diagrams-atlas')


    def test_sync_creates_navigable_knowledge_without_any_diagram(self):
        self.s.unlink()
        self.r.unlink()
        (self.w / "evidence" / "claims.json").write_text(json.dumps([
            {"id": "C-1", "kind": "entity", "status": "OBSERVED_CODE",
             "symbol_id": "A::handler", "query_ids": ["Q-1"]}]))
        (self.w / "evidence" / "queries.json").write_text(json.dumps([{"id": "Q-1"}]))
        result = atlas.build(self.repo, home=self.home)
        self.assertEqual(result["claims"], 1)
        content = Path(result["markdown"]).read_text()
        self.assertIn("A::handler", content)
        self.assertIn("claims.json", content)
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "CURRENT")

    def test_new_claim_or_view_invalidates_atlas_and_rebuilds(self):
        atlas.build(self.repo, home=self.home)
        c = self.w / "evidence" / "claims.json"
        c.write_text(json.dumps([{"id": "C-2", "kind": "relation", "status": "observed",
                                  "from_symbol": "A::run", "to_symbol": "B::save",
                                  "relation_source": "reference_link"}]))
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "STALE")
        atlas.build(self.repo, home=self.home)
        report = self.w / "lenses" / "c4" / "reports" / "context.atlas.json"
        c.write_text(json.dumps([{"id": "C-2", "kind": "entity", "status": "observed",
                                  "symbol_id": "A::run", "query_ids": ["Q-2"]}]))
        (self.w / "evidence" / "queries.json").write_text(json.dumps([
            {"id": "Q-2", "mode": "structured", "status": "ok", "symbol_ids": ["A::run"]}]))
        report.write_text(json.dumps({
            "schema_version": 1, "label": "Contexto",
            "claim_ids": ["C-2"],
            "assets": ["lenses/c4/sources/workspace.dsl", "lenses/c4/renders/context.svg"]}))
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "STALE")
        result = atlas.build(self.repo, home=self.home)
        self.assertIn("A::run", Path(result["markdown"]).read_text())
        self.assertIn("context.svg", Path(result["markdown"]).read_text())
        self.assertEqual(result["linked_views"], 1)

    def test_view_claim_and_asset_must_be_real_and_local(self):
        (self.w / "evidence" / "claims.json").write_text(json.dumps([
            {"id": "C-3", "kind": "entity", "status": "observed", "symbol_id": "A"}]))
        report = self.w / "lenses" / "c4" / "reports" / "x.atlas.json"
        report.write_text(json.dumps({"schema_version": 1, "label": "X",
                                      "claim_ids": ["invented"],
                                      "assets": ["lenses/c4/renders/context.svg"]}))
        with self.assertRaises(atlas.KnowledgeError):
            atlas.build(self.repo, home=self.home)
        report.write_text(json.dumps({"schema_version": 1, "label": "X",
                                      "claim_ids": ["C-3"], "assets": ["../../secret"]}))
        with self.assertRaises(atlas.KnowledgeError):
            atlas.build(self.repo, home=self.home)

    def test_evidence_symlink_and_unknown_query_rejected(self):
        p = self.w / "evidence" / "claims.json"
        p.symlink_to(self.repo / ".git" / "HEAD")
        with self.assertRaises(atlas.KnowledgeError):
            atlas.build(self.repo, home=self.home)
        p.unlink()
        p.write_text(json.dumps([{"id": "C-4", "kind": "entity", "status": "observed",
                                  "symbol_id": "A", "query_ids": ["Q-404"]}]))
        (self.w / "evidence" / "queries.json").write_text("[]")
        with self.assertRaises(atlas.KnowledgeError):
            atlas.build(self.repo, home=self.home)


    def test_semantic_categories_have_traceable_provenance(self):
        (self.w / "evidence" / "queries.json").write_text(json.dumps([{"id": "Q-1"}]))
        (self.w / "evidence" / "claims.json").write_text(json.dumps([
            {"id": "C-A", "kind": "entity", "status": "OBSERVED_CODE",
             "category": "surface", "symbol_id": "Grpc::serve", "coverage": "partial",
             "query_ids": ["Q-1"], "plane": "static"},
            {"id": "C-B", "kind": "relation", "status": "OBSERVED_CODE", "category": "external",
             "from_symbol": "Client::send", "to_symbol": "Server::accept",
             "query_ids": ["Q-1"], "coverage": "unknown",
             "attributes": {"technology": "gRPC"}}]))
        output = atlas.build(self.repo, home=self.home)
        content = Path(output["markdown"]).read_text()
        self.assertIn("Superficies", content)
        self.assertIn("Sistemas externos", content)
        self.assertIn("Q-1", content)
        self.assertIn("cobertura:partial", content)
        self.assertIn("gRPC", content)

    def test_intention_separate_and_cannot_justify_implemented_diagram(self):
        c = self.w / "evidence" / "claims.json"
        c.write_text(json.dumps([{"id": "I-1", "kind": "entity", "category": "intent",
                                  "provenance": "CURATED_INTENT", "curator": "usuario",
                                  "symbol_id": "Objetivo declarado", "plane": "intent"}]))
        result = atlas.build(self.repo, home=self.home)
        self.assertIn("NO demuestra implementacion", Path(result["markdown"]).read_text())
        view = self.w / "lenses" / "c4" / "reports" / "bad.atlas.json"
        view.write_text(json.dumps({"schema_version": 1, "label": "Falso",
                                    "claim_ids": ["I-1"], "assets": ["lenses/c4/renders/context.svg"]}))
        with self.assertRaises(atlas.KnowledgeError):
            atlas.build(self.repo, home=self.home)

    def test_code_doc_without_cognicode_ledger_is_not_certified(self):
        (self.w / "evidence" / "claims.json").write_text(json.dumps([
            {"id": "I-DOC", "kind": "entity", "category": "intent",
             "provenance": "CODE_DOC", "plane": "intent",
             "symbol_id": "Service KDoc", "query_ids": ["Q-77"]}]))
        r = atlas.build(self.repo, home=self.home)
        content = Path(r["markdown"]).read_text()
        self.assertIn("UNKNOWN  sin query", content)
        self.assertIn("NO demuestra implementacion", content)

    def test_doc_intent_requires_separate_explicit_mode(self):
        (self.w / "evidence" / "claims.json").write_text(json.dumps([
            {"id": "I-2", "kind": "entity", "category": "intent",
             "status": "DOC_INTENT", "symbol_id": "documentacion externa"}]))
        with self.assertRaises(atlas.KnowledgeError):
            atlas.build(self.repo, home=self.home)

    def test_una_observacion_sin_corroborar_no_se_declara_desconocida(self):
        # It was observed; nothing corroborates it. Publishing it as
        # "unknown" would deny what happened, and publishing it as plain
        # OBSERVED_CODE would overstate it. Both facts go out together.
        (self.w / "evidence" / "claims.json").write_text(json.dumps([
            {"id": "C-LEGACY", "kind": "entity", "symbol_id": "Legacy::entry",
             "status": "OBSERVED_CODE"}]))
        out = atlas.build(self.repo, home=self.home)
        content = Path(out["markdown"]).read_text()
        self.assertIn("OBSERVED CODE  sin corroborar", content)
        self.assertNotIn("UNKNOWN  sin corroborar", content)

    def test_sync_is_idempotent_with_unchanged_claim_ledger(self):
        (self.w / "evidence" / "claims.json").write_text(json.dumps([
            {"id": "C-5", "kind": "entity", "status": "observed", "symbol_id": "A"}]))
        result = atlas.build(self.repo, home=self.home)
        md = Path(result["markdown"])
        before = md.stat().st_mtime_ns
        atlas.build(self.repo, home=self.home)
        self.assertEqual(md.stat().st_mtime_ns, before)


    def test_unverified_claim_cannot_be_linked_as_implementation(self):
        ledger = self.w / "evidence/claims.json"
        queries = self.w / "evidence/queries.json"
        view = self.w / "lenses/c4/reports/invalid.atlas.json"
        ledger.write_text(json.dumps([{"id": "X", "kind": "entity",
                                       "status": "INFERRED", "symbol_id": "No::code"}]))
        view.write_text(json.dumps({"schema_version": 1, "label": "Wrong",
                                    "claim_ids": ["X"], "assets": ["lenses/c4/renders/context.svg"]}))
        with self.assertRaisesRegex(atlas.KnowledgeError, "corroborated"):
            atlas.build(self.repo, home=self.home)
        ledger.write_text(json.dumps([{"id": "X", "kind": "entity",
                                       "status": "OBSERVED_CODE", "symbol_id": "No::code",
                                       "query_ids": ["Q-X"]}]))
        queries.write_text(json.dumps([{"id": "Q-X", "mode": "structured", "status": "failed",
                                       "symbol_ids": ["No::code"]}]))
        with self.assertRaisesRegex(atlas.KnowledgeError, "corroborated"):
            atlas.build(self.repo, home=self.home)
        queries.write_text(json.dumps([{"id": "Q-X", "mode": "structured", "status": "ok",
                                       "symbol_ids": ["No::code"], "source": "cognicode"}]))
        atlas.build(self.repo, home=self.home)

    def test_router_supports_atlas_from_claims_before_diagrams(self):
        import affordances
        result = affordances.affordances({"intent": "atlas", "workspace": "ready",
               "atlas_assets": "absent", "atlas_claims_ready": True, "atlas_source": "absent"})
        self.assertEqual(result["recommended"], "build-atlas")

    def test_atlas_discovers_derived_inputs_once_per_sync(self):
        import knowledge_atlas
        with patch.object(knowledge_atlas, "inputs", wraps=knowledge_atlas.inputs) as discovered:
            atlas.build(self.repo, home=self.home)
        self.assertEqual(discovered.call_count, 1)

    def test_html_render_requires_current_atlas(self):
        with self.assertRaises(render_markmap.RenderError):
            render_markmap.render(self.repo,home=self.home)

    def test_generated_atlas_has_world_readable_static_mode(self):
        r = atlas.build(self.repo, home=self.home)
        self.assertEqual(Path(r["markdown"]).stat().st_mode & 0o777, 0o644)
        self.assertEqual(Path(r["manifest"]).stat().st_mode & 0o777, 0o644)

    def test_html_render_native_fake_markmap_and_no_network(self):
        atlas.build(self.repo,home=self.home)
        fake=subprocess.CompletedProcess(args=['markmap'],returncode=0,stdout='',stderr='')
        def run(cmd):
            Path(cmd[-1]).write_text('<html><script>hi</script></html>')
            return fake
        with patch.object(render_markmap.shutil,'which',return_value='/usr/bin/markmap'),patch.object(render_markmap,'_run',side_effect=run):
            r=render_markmap.render(self.repo,home=self.home,engine='native')
        self.assertEqual(r['status'],'RENDERED_NOT_VISUALLY_REVIEWED')
        self.assertTrue(Path(r['html']).read_text().startswith('<!-- cognicode-diagrams markmap -->'))
        self.assertEqual(Path(r['html']).stat().st_mode & 0o777, 0o644)

    def test_html_failure_preserves_existing(self):
        atlas.build(self.repo,home=self.home)
        with patch.object(render_markmap.shutil,'which',return_value='/usr/bin/markmap'),patch.object(render_markmap,'_run',return_value=subprocess.CompletedProcess(['markmap'],1,'','failed')):
            with self.assertRaises(render_markmap.RenderError):
                render_markmap.render(self.repo,home=self.home,engine='native')
        self.assertFalse((self.w/'navigation'/'atlas.html').exists())

    def test_container_does_not_mount_repo_and_default_network_off(self):
        atlas.build(self.repo,home=self.home)
        def run(cmd):
            self.assertIn('--network',cmd)
            self.assertEqual(cmd[cmd.index('--network')+1],'none')
            self.assertIn(f'{self.w}:/data:ro,z',cmd)
            self.assertIn('--userns=keep-id', cmd)
            self.assertNotIn(str(self.repo), ' '.join(cmd))
            fname=cmd[-1].split('/')[-1]
            (self.w/'navigation'/fname).write_text('<html><script>hi</script></html>')
            return subprocess.CompletedProcess(cmd,0,'','')
        with patch.object(render_markmap.shutil,'which',return_value='/usr/bin/podman'),patch.object(render_markmap,'_run',side_effect=run):
            r=render_markmap.render(self.repo,home=self.home,engine='podman')
        self.assertEqual(r['status'],'RENDERED_NOT_VISUALLY_REVIEWED')

    def test_render_rejects_ungenerated_html(self):
        atlas.build(self.repo,home=self.home)
        (self.w/'navigation'/'atlas.html').write_text('existing user data')
        with self.assertRaises(render_markmap.RenderError):
            render_markmap.render(self.repo,home=self.home,engine='native')


if __name__ == '__main__':
    unittest.main()

# Cross-lens atlas flow is independent from C4 lens and CogniCode runtime.
import affordances

class AtlasRoutingTests(unittest.TestCase):
    def test_uninitialized_workspace_gates_atlas(self):
        r = affordances.affordances({'intent':'atlas','workspace':'unknown'})
        self.assertEqual(r['recommended'], 'inspect-workspace')

    def test_missing_assets_blocks(self):
        r=affordances.affordances({'intent':'atlas','workspace':'ready','atlas_assets':'absent'})
        self.assertEqual(r['status'],'BLOCKED')

    def test_atlas_does_not_need_lens_or_mcp(self):
        r=affordances.affordances({'intent':'atlas','workspace':'ready','atlas_assets':'present','atlas_source':'absent'})
        self.assertEqual(r['recommended'],'build-atlas')

    def test_stale_atlas_rebuilt(self):
        r=affordances.affordances({'intent':'atlas','workspace':'ready','atlas_source':'stale'})
        self.assertEqual(r['recommended'],'build-atlas')

    def test_render_without_markmap_does_not_claim_done(self):
        r=affordances.affordances({'intent':'atlas','workspace':'ready','atlas_source':'ready','markmap':'missing'})
        self.assertEqual(r['status'],'PARTIAL')

    def test_html_rendered_needs_visual_review(self):
        r=affordances.affordances({'intent':'atlas','workspace':'ready','atlas_source':'ready','atlas_html':'rendered'})
        self.assertEqual(r['recommended'],'open-atlas')

    def test_review_verified_only_as_visual(self):
        r=affordances.affordances({'intent':'atlas','workspace':'ready','atlas_source':'ready','atlas_html':'rendered','visual_review':'passed'})
        self.assertEqual(r['status'],'VERIFIED')
        self.assertEqual(r['recommended'],'finish')
