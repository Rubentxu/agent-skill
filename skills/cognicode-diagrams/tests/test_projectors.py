"""Tests sin contenedores reales: políticas de seguridad + comandos OCI."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
spec = importlib.util.spec_from_file_location('diagrams_projectors', SKILL / 'scripts/projectors.py')
engine = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = engine
spec.loader.exec_module(engine)
import workspace


class ProjectorTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        base = Path(t.name)
        self.home = base / 'home'
        self.home.mkdir()
        self.repo = base / 'repos' / 'pipelinek'
        self.repo.mkdir(parents=True)
        subprocess.run(['git','init','-q',str(self.repo)],check=True)
        info = workspace.init(self.repo, home=self.home)
        self.external = Path(info['workspace'])
        self.sources = Path(workspace.init_lens(self.repo, 'c4', home=self.home)['lens_path']) / 'sources'
        self.struct = self.sources / 'workspace.dsl'
        self.struct.write_text('workspace "Example" { model {} views {} }', encoding='utf-8')
        self.likec4 = self.sources / 'model.c4'
        self.likec4.write_text('specification { element actor }\nmodel { actor user }\nviews { view index { include * } }',encoding='utf-8')
        self.p = engine.params(self.repo, 'structurizr', home=self.home)

    def test_bound_to_home_not_git(self):
        self.assertTrue(Path(self.p['source']).is_relative_to(self.home))
        self.assertFalse(Path(self.p['source']).is_relative_to(self.repo))
        self.assertEqual(self.p['lens'], 'c4')

    def test_source_missing_fails_before_runtime(self):
        self.struct.unlink()
        with self.assertRaises(engine.ProjectorError):
            engine.verify_sources(self.p)

    def test_likec4_requires_c4_file(self):
        p = engine.params(self.repo,'likec4',home=self.home)
        self.likec4.unlink()
        with self.assertRaises(engine.ProjectorError):
            engine.verify_sources(p)

    def test_rejects_workspace_symlink(self):
        self.sources.rename(self.sources.with_name('real'))
        self.sources.symlink_to(self.sources.with_name('real'), target_is_directory=True)
        with self.assertRaises(engine.ProjectorError):
            engine.params(self.repo,'structurizr',home=self.home)

    def test_markmap_projector_uses_readonly_external_workspace(self):
        p = engine.params(self.repo, "markmap", home=self.home)
        self.assertEqual(p["source"], str(self.external))
        nav = self.external / "navigation"
        nav.mkdir(exist_ok=True)
        import hashlib
        from atlas import build as build_atlas
        build_atlas(self.repo, home=self.home)
        digest = hashlib.sha256((nav / "atlas.md").read_bytes()).hexdigest()
        (nav / "atlas.html").write_text(
            "<!-- cognicode-diagrams markmap -->\n"
            + f"<!-- atlas-source-sha256:{digest} -->\n<html></html>")
        engine.verify_sources(p)
        commands = []
        def fake(_engine, args, **kwargs):
            commands.append(args)
            return subprocess.CompletedProcess(args, 0, "cid", "")
        with patch.object(engine, "existing", return_value=None), \
             patch.object(engine, "run_engine", side_effect=fake), \
             patch.object(engine, "status", return_value={"status": "running_unverified"}):
            engine.start("podman", p, port=4173, hmr_port=24678)
        cmd = commands[0]
        self.assertIn("127.0.0.1:4173:4173", cmd)
        self.assertIn(p["source"] + ":/data:ro,z", cmd)
        self.assertIn("--read-only", cmd)
        self.assertIn("--cap-drop", cmd)
        self.assertNotIn(str(self.repo), " ".join(x for x in cmd if x != engine.MARKMAP_SERVER))

    def test_markmap_requires_previously_generated_html(self):
        p = engine.params(self.repo, "markmap", home=self.home)
        with self.assertRaises(engine.ProjectorError):
            engine.verify_sources(p)


    def test_old_markmap_html_is_refused_after_evidence_update(self):
        from atlas import build as build_atlas
        import hashlib
        build_atlas(self.repo, home=self.home)
        p = engine.params(self.repo, "markmap", home=self.home)
        html = self.external / "navigation/atlas.html"
        digest = hashlib.sha256((self.external / "navigation/atlas.md").read_bytes()).hexdigest()
        html.write_text("<!-- cognicode-diagrams markmap -->\n"
                        + f"<!-- atlas-source-sha256:{digest} -->\n<html></html>")
        engine.verify_sources(p)
        (self.external / "evidence/claims.json").write_text("[]")
        with self.assertRaisesRegex(engine.ProjectorError, "evidencia actual"):
            engine.verify_sources(p)
        build_atlas(self.repo, home=self.home)
        with self.assertRaisesRegex(engine.ProjectorError, "obsoleto"):
            engine.verify_sources(p)

    def test_local_server_allowlists_generated_navigation_and_rejects_traversal(self):
        import threading
        from http.server import ThreadingHTTPServer
        from urllib.request import urlopen
        from urllib.error import HTTPError
        import hashlib
        namespace = {"__name__": "viewer_contract_test"}
        exec(engine.MARKMAP_SERVER, namespace)
        namespace["ROOT"] = self.external
        nav = self.external / "navigation"
        nav.mkdir(exist_ok=True)
        body = b"<!-- Generated by cognicode-diagrams atlas.py. Do not edit -->\n# Atlas\n"
        (nav / "atlas.md").write_bytes(body)
        digest = hashlib.sha256(body).hexdigest()
        (nav / "atlas.html").write_text("<!-- cognicode-diagrams markmap -->\n"
                                        + f"<!-- atlas-source-sha256:{digest} -->\n<html></html>")
        path = self.external / "reports/term-card-0123456789abcdef.report.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text("OK")
        server = ThreadingHTTPServer(("127.0.0.1", 0), namespace["Handler"])
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}"
            self.assertIn(b"OK", urlopen(url + "/reports/term-card-0123456789abcdef.report.md").read())
            self.assertIn(b"atlas-source-sha256", urlopen(url).read())
            with self.assertRaises(HTTPError) as forbidden:
                urlopen(url + "/../src/private.txt")
            self.assertEqual(forbidden.exception.code, 404)
            (nav / "atlas.md").write_text("different")
            with self.assertRaises(HTTPError) as stale:
                urlopen(url + "/navigation/atlas.html")
            self.assertEqual(stale.exception.code, 409)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_default_engine_prefers_podman(self):
        with patch.object(engine.shutil,'which', side_effect=lambda x: '/usr/bin/'+x):
            self.assertEqual(engine.engine_binary(None),'podman')

    def test_explicit_engine_failure(self):
        with patch.object(engine.shutil,'which',return_value=None):
            with self.assertRaises(engine.ProjectorError):
                engine.engine_binary('podman')

    def test_engine_allowlist(self):
        with self.assertRaises(engine.ProjectorError):
            engine.engine_binary('curl')

    def test_invalid_port(self):
        for port in (0,80,65536):
            with self.assertRaises(engine.ProjectorError):
                engine.port_number(port)

    def test_inspect_does_not_start_container(self):
        def fake(_engine,args,**kwargs):
            self.assertEqual(args[:2],['inspect',self.p['name']])
            return subprocess.CompletedProcess(args,1,'','Error: no such container')
        with patch.object(engine,'run_engine',side_effect=fake):
            self.assertEqual(engine.status('podman',self.p)['status'],'missing')

    def test_inspect_fails_closed_on_permission_error(self):
        with patch.object(engine,'run_engine',return_value=subprocess.CompletedProcess([],125,'','permission denied')):
            with self.assertRaises(engine.ProjectorError):
                engine.existing('podman',self.p)

    def test_rejects_unowned_container(self):
        data = [{'Config':{'Labels':{engine.LABEL_WORKSPACE:'/other',engine.LABEL_PROJECTOR:'structurizr'}},'State':{'Running':True}}]
        with patch.object(engine,'run_engine',return_value=subprocess.CompletedProcess([],0,json.dumps(data),'') ):
            with self.assertRaises(engine.ProjectorError):
                engine.existing('podman',self.p)

    def test_existing_owned_metadata(self):
        labels = {engine.LABEL_WORKSPACE:self.p['workspace'],engine.LABEL_PROJECTOR:'structurizr',engine.LABEL_LENS:'c4',engine.LABEL_PORT:'8080'}
        data = [{'Config':{'Labels':labels},'State':{'Running':True},
                 'Mounts':[{'Source':self.p['source'],'Destination':'/usr/local/structurizr'}],
                 'HostConfig':{'PortBindings':{'8080/tcp':[{'HostIp':'127.0.0.1','HostPort':'8080'}]}}}]
        with patch.object(engine,'run_engine',return_value=subprocess.CompletedProcess([],0,json.dumps(data),'') ):
            self.assertEqual(engine.status('podman',self.p)['status'],'running')

    def test_prevent_reusing_container_mounting_repo(self):
        labels={engine.LABEL_WORKSPACE:self.p['workspace'],engine.LABEL_PROJECTOR:'structurizr',
                engine.LABEL_LENS:'c4',engine.LABEL_PORT:'8080'}
        data=[{'Config':{'Labels':labels},'State':{'Running':True},
               'Mounts':[{'Source':str(self.repo),'Destination':'/usr/local/structurizr'}],
               'HostConfig':{'PortBindings':{'8080/tcp':[{'HostIp':'127.0.0.1','HostPort':'8080'}]}}}]
        with patch.object(engine,'run_engine',return_value=subprocess.CompletedProcess([],0,json.dumps(data),'')):
            with self.assertRaises(engine.ProjectorError):
                engine.existing('podman',self.p)

    def test_prevent_reusing_publicly_exposed_container(self):
        labels={engine.LABEL_WORKSPACE:self.p['workspace'],engine.LABEL_PROJECTOR:'structurizr',
                engine.LABEL_LENS:'c4',engine.LABEL_PORT:'8080'}
        data=[{'Config':{'Labels':labels},'State':{'Running':True},
               'Mounts':[{'Source':self.p['source'],'Destination':'/usr/local/structurizr'}],
               'HostConfig':{'PortBindings':{'8080/tcp':[{'HostIp':'0.0.0.0','HostPort':'8080'}]}}}]
        with patch.object(engine,'run_engine',return_value=subprocess.CompletedProcess([],0,json.dumps(data),'')):
            with self.assertRaises(engine.ProjectorError):
                engine.existing('podman',self.p)

    def test_start_structurizr_is_visual_only(self):
        commands=[]
        def fake(_engine,args,**kwargs):
            commands.append(args)
            if args[0]=='run':return subprocess.CompletedProcess(args,0,'container-id','')
            raise AssertionError(args)
        with patch.object(engine,'existing',return_value=None), patch.object(engine,'run_engine',side_effect=fake), patch.object(engine,'status',return_value={'status':'running_unverified'}):
            engine.start('podman',self.p,port=8080,hmr_port=24678)
        cmd=commands[0]
        self.assertEqual(cmd[0],'run')
        self.assertIn('127.0.0.1:8080:8080',cmd)
        self.assertIn(self.p['source']+':/usr/local/structurizr:z',cmd)
        self.assertIn('STRUCTURIZR_EDITABLE=false',cmd)
        self.assertIn('STRUCTURIZR_AUTOSAVEINTERVAL=0',cmd)
        self.assertNotIn(str(self.repo),str(cmd))
        self.assertEqual(cmd[-1],'local')

    def test_start_likec4_adds_local_hmr(self):
        p=engine.params(self.repo,'likec4',home=self.home)
        commands=[]
        def fake(_engine,args,**kwargs):
            commands.append(args)
            return subprocess.CompletedProcess(args,0,'container-id','')
        with patch.object(engine,'existing',return_value=None), patch.object(engine,'run_engine',side_effect=fake), patch.object(engine,'status',return_value={'status':'running_unverified'}):
            engine.start('podman',p,port=5173,hmr_port=24678)
        self.assertIn('127.0.0.1:5173:5173',commands[0]);self.assertIn('127.0.0.1:24678:24678',commands[0])
        self.assertIn(p['source']+':/data:z',commands[0]); self.assertIn('likec4/likec4:latest',commands[0]);self.assertNotIn(str(self.repo),str(commands[0]))

    def test_start_existing_wrong_ports_refused(self):
        with patch.object(engine,'existing',return_value={'running':False,'labels':{engine.LABEL_PORT:'4000'}}),patch.object(engine,'run_engine') as run:
            with self.assertRaises(engine.ProjectorError):engine.start('podman',self.p,port=8080,hmr_port=24678)
            run.assert_not_called()

    def test_stop_only_named_owned_container(self):
        operations=[]
        def fake(_engine,args,**kwargs):
            operations.append(args)
            return subprocess.CompletedProcess(args,0,'','')
        with patch.object(engine,'existing',return_value={'running':True,'labels':{}}),patch.object(engine,'run_engine',side_effect=fake),patch.object(engine,'status',return_value={'status':'stopped'}):
            engine.stop_or_remove('podman',self.p,remove=False)
        self.assertEqual(operations,[['stop',self.p['name']]])

    def test_remove_is_explicit_not_implicit(self):
        operations=[]
        def fake(_engine,args,**kwargs):
            operations.append(args)
            return subprocess.CompletedProcess(args,0,'','')
        with patch.object(engine,'existing',return_value={'running':True,'labels':{}}),patch.object(engine,'run_engine',side_effect=fake),patch.object(engine,'status',return_value={'status':'missing'}):
            engine.stop_or_remove('podman',self.p,remove=True)
        self.assertEqual(operations,[['stop',self.p['name']],['rm',self.p['name']]])

    def test_no_source_changes_git(self):
        with patch.object(engine,'existing',return_value=None), patch.object(engine,'run_engine',return_value=subprocess.CompletedProcess([],0,'ok','')), patch.object(engine,'status',return_value={'status':'running_unverified'}):
            engine.start('podman',self.p,port=8080,hmr_port=24678)
        self.assertEqual(subprocess.check_output(['git','-C',str(self.repo),'status','--porcelain'],text=True),'')

    def test_per_lens_isolation(self):
        workspace.init_lens(self.repo, 'vertical-slice',home=self.home)
        p=engine.params(self.repo,'likec4',lens='vertical-slice',home=self.home)
        self.assertEqual(p['lens'],'vertical-slice')
        self.assertNotEqual(p['name'], engine.params(self.repo,'likec4',home=self.home)['name'])
        self.assertTrue(Path(p['source']).is_relative_to(self.external))


if __name__=='__main__': unittest.main()
