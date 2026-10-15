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

    def test_html_render_requires_current_atlas(self):
        with self.assertRaises(render_markmap.RenderError):
            render_markmap.render(self.repo,home=self.home)

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
