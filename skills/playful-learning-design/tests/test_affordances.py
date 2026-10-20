import importlib.util, pathlib, unittest
PATH=pathlib.Path(__file__).resolve().parents[1]/'scripts'/'affordances.py'
spec=importlib.util.spec_from_file_location('lgs_design_aff',PATH)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RouterTests(unittest.TestCase):
 def test_catalog(self): self.assertEqual(m.decide({'intent':'catalog'})['rel'],'list-lenses')
 def test_missing_audience(self): self.assertIn('learner-context',m.decide({'intent':'design'})['href'])
 def test_objective_first(self): self.assertIn('learning-loop',m.decide({'intent':'design','audience':'ready'})['href'])
 def test_choose_game(self):
  s={'intent':'design','audience':'ready','objective':'ready','knowledge':'ready'}
  self.assertIn('mechanic-selection',m.decide(s)['href'])
 def test_focus_after_preconditions(self):
  s={'intent':'refine','audience':'ready','objective':'ready','knowledge':'ready','focus':'rewards','motivation':'missing'}
  self.assertIn('ethical-motivation',m.decide(s)['href'])
 def test_deliver(self):
  s={'intent':'design',**{x['signal']:'ready' for x in __import__('json').loads(m.REG.read_text())['lenses']}}
  self.assertEqual(m.decide(s)['rel'],'deliver-brief')
 def test_invalid(self):
  with self.assertRaises(ValueError): m.decide({'intent':'design','audience':'PASSED'})
 def test_existing_links(self):
  s={'intent':'catalog'}
  self.assertTrue((m.ROOT/m.decide(s)['href']).is_file())
if __name__=='__main__':unittest.main()
