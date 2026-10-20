#!/usr/bin/env python3
"""Selector puro de siguiente guía desde ESTADO OBSERVADO. No ejecuta ni certifica nada."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'references/lens-registry.json'
SEQUENCE=['learner-context','learning-loop','knowledge-and-misconceptions','mechanic-selection','novice-scaffolding','ethical-motivation','learning-evidence','inclusive-design']
INTENTS={'catalog','design','refine','audit'}
STATES={'ready','missing','unknown'}

def decide(s):
    if not isinstance(s,dict) or s.get('intent') not in INTENTS: raise ValueError('intent invalid')
    items={x['id']:x for x in json.loads(REG.read_text(encoding='utf8'))['lenses']}
    if s['intent']=='catalog': return {'rel':'list-lenses','href':'references/lens-registry.json','why':'inspect available lenses'}
    focus={'content':'knowledge-and-misconceptions','game':'mechanic-selection','explanation':'novice-scaffolding','rewards':'ethical-motivation','assessment':'learning-evidence','inclusion':'inclusive-design'}.get(s.get('focus'))
    order=SEQUENCE
    if focus and s.get('audience')=='ready' and s.get('objective')=='ready' and s.get('knowledge')=='ready':
        order=[focus]+[x for x in SEQUENCE if x!=focus]
    for id in order:
        entry=items[id]
        status=s.get(entry['signal'],'unknown')
        if status not in STATES: raise ValueError('invalid state '+entry['signal'])
        if status!='ready':
            if entry['status']!='ready':return {'rel':'blocked','href':'references/navigation.md','why':'lens planned: '+id}
            return {'rel':'inspect-'+id,'href':entry['playbook'],'why':entry['signal']+'='+status}
    return {'rel':'deliver-brief','href':'assets/learning-experience-brief.md','why':'inputs declared ready; ensure evidence before claims'}

if __name__=='__main__':
    s=json.load(sys.stdin) if len(sys.argv)<2 or sys.argv[1]=='-' else json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
    result=decide(s)
    if not (ROOT/result['href']).is_file(): raise SystemExit('broken local ref '+result['href'])
    print(json.dumps({'_links':[result]},ensure_ascii=False))
