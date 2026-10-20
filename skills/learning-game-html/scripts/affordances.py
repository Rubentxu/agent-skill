#!/usr/bin/env python3
"""Router puro de estados observados a guías locales. No ejecuta navegador ni certifica tests."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'references/lens-registry.json'
INTENTS={'catalog','create','improve','repair','polish','audit'}
STATES={'ready','missing','unknown'}
CHECKS={'passed','failed','not_run','blocked'}
ROUTES={
 'create':['brief','art','scene','state','storage','access','visual_review','browser_check','package'],
 'improve':['baseline','brief','state','art','scene','storage','access','visual_review','browser_check','package'],
 'repair':['baseline','brief','state','browser_check','storage','package'],
 'polish':['baseline','brief','art','scene','access','visual_review','browser_check','package'],
 'audit':['baseline','browser_check','visual_review']}

def decide(s):
 if not isinstance(s,dict) or s.get('intent') not in INTENTS:raise ValueError('invalid intent')
 cat={x['signal']:x for x in json.loads(REG.read_text(encoding='utf8'))['lenses']}
 if s['intent']=='catalog':return {'rel':'list-lenses','href':'references/lens-registry.json','why':'inspect catalogue'}
 for name in ROUTES[s['intent']]:
  if name=='storage' and s['intent']=='repair' and s.get('storage_affected') is not True: continue
  if name=='brief':
   status=s.get('brief','unknown')
   if status not in STATES:raise ValueError('invalid brief')
   if status!='ready':return {'rel':'resolve-brief','href':'assets/design-brief.md','why':f'brief={status}'}
   continue
  entry=cat[name]
  status=s.get(name,'not_run' if name in ('browser_check','visual_review') else 'unknown')
  if status not in (CHECKS if name in ('browser_check','visual_review') else STATES):raise ValueError('invalid '+name)
  done=status=='passed' if name in ('browser_check','visual_review') else status=='ready'
  if not done:
   if entry['status']!='ready':return {'rel':'blocked','href':'references/navigation.md','why':'lens planned: '+name}
   return {'rel':'inspect-'+entry['id'],'href':entry['playbook'],'why':name+'='+status}
 return {'rel':'deliver-artifact' if s['intent']!='audit' else 'deliver-audit','href':'references/navigation.md','why':'all declared stages ready; verify evidence identity'}

if __name__=='__main__':
 s=json.load(sys.stdin) if len(sys.argv)<2 or sys.argv[1]=='-' else json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
 result=decide(s)
 if not (ROOT/result['href']).is_file():raise SystemExit('invalid local href '+result['href'])
 print(json.dumps({'_links':[result]},ensure_ascii=False))
