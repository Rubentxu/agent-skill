import importlib.util,pathlib,unittest,json
PATH=pathlib.Path(__file__).resolve().parents[1]/'scripts'/'affordances.py'
spec=importlib.util.spec_from_file_location('lgs_html_aff',PATH)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RouterTests(unittest.TestCase):
 def test_catalog(self):self.assertEqual(m.decide({'intent':'catalog'})['rel'],'list-lenses')
 def test_create_starts_brief(self):self.assertEqual(m.decide({'intent':'create'})['rel'],'resolve-brief')
 def test_create_prioritizes_art(self):self.assertIn('art-direction',m.decide({'intent':'create','brief':'ready'})['href'])
 def test_repair_does_not_force_art(self):self.assertIn('baseline',m.decide({'intent':'repair','brief':'ready'})['href'])
 def test_repair_browser_critical(self):
  x={'intent':'repair','baseline':'ready','brief':'ready','state':'ready'}
  self.assertIn('browser-acceptance',m.decide(x)['href'])
 def test_repair_storage_when_risky(self):
  x={'intent':'repair','baseline':'ready','brief':'ready','state':'ready','browser_check':'passed','storage_affected':True}
  self.assertIn('progress-and-migration',m.decide(x)['href'])
 def test_polish(self):self.assertIn('art-direction',m.decide({'intent':'polish','baseline':'ready','brief':'ready'})['href'])
 def test_full_create(self):
  x={'intent':'create','brief':'ready',**{p:'ready' for p in ['art','scene','state','storage','access','package']},'visual_review':'passed','browser_check':'passed'}
  self.assertEqual(m.decide(x)['rel'],'deliver-artifact')
 def test_notrun_not_green(self):
  x={'intent':'create','brief':'ready',**{p:'ready' for p in ['art','scene','state','storage','access']},'visual_review':'not_run'}
  self.assertIn('visual-qa',m.decide(x)['href'])
 def test_invalid(self):
  with self.assertRaises(ValueError):m.decide({'intent':'create','brief':'PASSED'})
 def test_all_local_lenses(self):
  for e in json.loads(m.REG.read_text())['lenses']:self.assertTrue((m.ROOT/e['playbook']).is_file())
if __name__=='__main__':unittest.main()
