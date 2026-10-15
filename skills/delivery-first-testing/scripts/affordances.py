#!/usr/bin/env python3
"""Pure HATEOAS-like advisor; no execution, subprocesses, network, filesystem writes.

Usage: python3 scripts/affordances.py examples/session-feature.json
       python3 scripts/affordances.py - < session.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CATALOG = BASE / 'references' / 'lens-registry.json'
PEERS = BASE / 'references' / 'skill-registry.json'
SLUG = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')
INTENTS = {'catalog', 'feature', 'merge', 'integration', 'release', 'audit'}
INVENTORY = {'unknown', 'ready'}
IMPACT = {'unknown', 'known', 'none'}
BASIS = {'unknown', 'current', 'stale'}
RISKS = {'routine', 'high', 'critical'}
CHANGES = {'ui', 'domain', 'api', 'security', 'persistence', 'protocol', 'ci', 'release', 'docs', 'harness', 'unknown'}
CHECKS = {'not_run', 'passed', 'failed', 'blocked'}
UAT = {'pending', 'passed', 'failed', 'not_needed'}
REGRESSION = {'pending', 'decided'}
ARTIFACT = {'unknown', 'ready', 'missing'}
STATUSES = {'ready', 'planned'}

ACTIONS = {
    'list-lenses': 'references/extend-lenses.md',
    'inspect-project': 'references/lenses/change-impact.md',
    'refresh-basis': 'references/evidence.md',
    'resolve-impact': 'references/lenses/change-impact.md',
    'run-affected': 'references/lenses/change-impact.md',
    'classify-failure': 'references/lenses/failure-triage.md',
    'explore-uat': 'references/lenses/ephemeral-uat.md',
    'decide-regression': 'references/lenses/regression-promotion.md',
    'finish-feature': 'references/evidence.md',
    'run-merge': 'references/lenses/merge-assurance.md',
    'finish-merge': 'references/evidence.md',
    'run-integration': 'references/lenses/integration-assurance.md',
    'finish-integration': 'references/evidence.md',
    'inspect-artifact': 'references/lenses/release-assurance.md',
    'run-release': 'references/lenses/release-assurance.md',
    'finish-release': 'references/evidence.md',
    'audit-portfolio': 'references/lenses/harness-economics.md',
    'propose-lens': 'references/extend-lenses.md',
}


class InvalidState(ValueError):
    """Input or lens registry cannot safely be interpreted."""


def read_catalog(path: Path = CATALOG) -> dict[str, dict]:
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise InvalidState(f'Cannot read catalogue: {exc}') from exc
    if not isinstance(raw, dict) or raw.get('schema_version') != 1 or not isinstance(raw.get('lenses'), list):
        raise InvalidState('Unsupported registry schema')
    catalog: dict[str, dict] = {}
    for lens in raw['lenses']:
        if not isinstance(lens, dict) or not isinstance(lens.get('id'), str):
            raise InvalidState('Invalid lens entry')
        key = lens['id']
        if not SLUG.fullmatch(key) or key in catalog or lens.get('status') not in STATUSES:
            raise InvalidState(f'Invalid/duplicate lens {key!r}')
        if not isinstance(lens.get('intents'), list) or not lens['intents'] or any(i not in INTENTS for i in lens['intents']):
            raise InvalidState(f'Invalid intents in {key}')
        if not isinstance(lens.get('signals'), list) or any(s not in CHANGES for s in lens['signals']):
            raise InvalidState(f'Invalid signals in {key}')
        path_string = lens.get('playbook')
        if not isinstance(path_string, str) or not path_string.startswith('references/'):
            raise InvalidState(f'Invalid playbook of {key}')
        dest = (BASE / path_string).resolve()
        if not dest.is_relative_to(BASE.resolve()) or not dest.is_file():
            raise InvalidState(f'Unsafe or absent playbook for {key}')
        if lens['status'] == 'ready' and not path_string.startswith('references/lenses/'):
            raise InvalidState(f'Ready lens {key} lacks an active specialized playbook')
        catalog[key] = lens
    if not catalog:
        raise InvalidState('Empty catalog')
    return catalog


def enum_value(d: dict, key: str, allowed: set[str], default: str | None = None) -> str:
    val = d.get(key, default)
    if not isinstance(val, str) or val not in allowed:
        raise InvalidState(f'{key}: invalid/absent {val!r}')
    return val


def parse_state(state: dict) -> dict:
    if not isinstance(state, dict):
        raise InvalidState('state must be a JSON object')
    intent = enum_value(state, 'intent', INTENTS)
    if intent == 'catalog':
        return {'intent': intent}
    parsed = {
        'intent': intent,
        'inventory': enum_value(state, 'inventory', INVENTORY, 'unknown'),
        'impact': enum_value(state, 'impact', IMPACT, 'unknown'),
        'basis': enum_value(state, 'basis', BASIS, 'unknown'),
        'risk': enum_value(state, 'risk', RISKS, 'routine'),
        'affected': enum_value(state, 'affected', CHECKS, 'not_run'),
        'merge_checks': enum_value(state, 'merge_checks', CHECKS, 'not_run'),
        'integration_checks': enum_value(state, 'integration_checks', CHECKS, 'not_run'),
        'release_checks': enum_value(state, 'release_checks', CHECKS, 'not_run'),
        'uat': enum_value(state, 'uat', UAT, 'pending'),
        'regression': enum_value(state, 'regression', REGRESSION, 'pending'),
        'artifact': enum_value(state, 'artifact', ARTIFACT, 'unknown'),
    }
    changed = state.get('changed', [])
    if not isinstance(changed, list) or any(not isinstance(x, str) or x not in CHANGES for x in changed):
        raise InvalidState('changed must be an array of supported signals')
    parsed['changed'] = list(dict.fromkeys(changed))
    available = state.get('available_skills', [])
    if not isinstance(available, list) or any(not isinstance(v,str) or not SLUG.fullmatch(v) for v in available):
        raise InvalidState('available_skills must be a list of skill identifiers')
    parsed['available_skills'] = list(dict.fromkeys(available))
    lens_gap = state.get('lens_gap', False)
    if not isinstance(lens_gap, bool):
        raise InvalidState('lens_gap must be boolean')
    parsed['lens_gap'] = lens_gap
    for label in ('uat_reason', 'regression_reason', 'evidence_commit'):
        val = state.get(label, '')
        if not isinstance(val, str):
            raise InvalidState(f'{label} must be a string')
        parsed[label] = val.strip()
    if parsed['uat'] == 'not_needed' and not parsed['uat_reason']:
        raise InvalidState('not_needed requires uat_reason')
    if parsed['regression'] == 'decided' and not parsed['regression_reason']:
        raise InvalidState('decided requires regression_reason')
    return parsed


def recommended_lenses(parsed: dict, catalog: dict[str, dict]) -> list[dict]:
    intent = parsed['intent']
    if intent == 'catalog':
        return []
    signals = set(parsed['changed'])
    routed = []
    for lens in catalog.values():
        if lens['status'] != 'ready' or intent not in lens['intents']:
            continue
        if lens['id'] == 'failure-triage' and not any(parsed[k] in {'failed', 'blocked'} for k in ('affected','merge_checks','integration_checks','release_checks')) and parsed['uat'] != 'failed':
            continue
        if lens['id'] == 'ephemeral-uat' and parsed['uat'] == 'not_needed':
            continue
        if lens['id'] == 'harness-economics' and intent != 'audit' and not signals.intersection({'harness', 'ci'}):
            continue
        # A lens with signals is still relevant when it owns the intent and is
        # essential even if the caller cannot classify individual paths yet.
        routed.append({'id': lens['id'], 'playbook': lens['playbook'], 'question': lens['question']})
    return routed


def suggested_peers(parsed: dict) -> list[dict]:
    if parsed['intent'] == 'catalog':
        return []
    try:
        data = json.loads(PEERS.read_text(encoding='utf-8'))
    except (ValueError, OSError) as exc:
        raise InvalidState(f'Cannot read peer catalog: {exc}') from exc
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('related_skills'), list):
        raise InvalidState('Invalid skill registry')
    peers=[]
    for item in data['related_skills']:
        if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not SLUG.fullmatch(item['id']):
            raise InvalidState('Invalid related skill')
        if (item['id'] in parsed['available_skills'] and parsed['intent'] in item['intents']
                and (not item['signals'] or set(parsed['changed']) & set(item['signals']))):
            peers.append({'rel':'consider-skill','id':item['id'],
                          'guide':'references/related-skills.md', 'why':item['purpose']})
    return peers


def affordances(state: dict, catalog: dict[str, dict] | None = None) -> dict:
    cat = read_catalog() if catalog is None else catalog
    s = parse_state(state)
    if s['intent'] == 'catalog':
        return {
            'intent': 'catalog', 'status': 'READY', 'recommended': 'list-lenses',
            '_links': [{'rel':'list-lenses','href':ACTIONS['list-lenses'],'why':'Browse available and planned lenses'}],
            'lenses': [{'id':l['id'],'status':l['status'],'question':l['question']} for l in cat.values()],
        }
    lenses = recommended_lenses(s, cat)
    peers = suggested_peers(s)
    gap = s['lens_gap'] or 'unknown' in s['changed']

    def result(rel: str, status: str, why: str) -> dict:
        if rel not in ACTIONS:
            raise InvalidState(f'Unknown action {rel}')
        path = (BASE / ACTIONS[rel]).resolve()
        if not path.is_file() or not path.is_relative_to(BASE.resolve()):
            raise InvalidState(f'Action target absent/unsafe: {rel}')
        return {
            'intent': s['intent'], 'status': status, 'recommended': rel,
            '_links': [{'rel': rel, 'href': ACTIONS[rel], 'why': why}],
            'lenses': lenses,
            'related_skills': peers,
            'discovery': [{'rel':'propose-lens','href':ACTIONS['propose-lens'], 'why':'Investigate unmatched guarantees; does not activate a new lens'}] if gap else [],
            'notice': 'Decision aid only; no suite executed and no evidence verified',
        }
    if s['inventory'] != 'ready':
        return result('inspect-project', 'NEEDS_EVIDENCE', 'Observe real build, tests, tools and risk before planning')
    if s['basis'] != 'current':
        return result('refresh-basis', 'NEEDS_EVIDENCE', 'Evidence must match current revision/context')
    if s['intent'] in ('feature', 'merge') and s['impact'] == 'unknown':
        return result('resolve-impact', 'NEEDS_EVIDENCE', 'Determine affected contracts and consumers')

    if s['intent'] == 'feature':
        if s['affected'] == 'failed' or s['uat'] == 'failed':
            return result('classify-failure', 'FAILED', 'Distinguish product defect, outdated test and stale evidence')
        if s['affected'] == 'blocked':
            return result('classify-failure', 'BLOCKED', 'Investigate missing runnable evidence')
        if s['affected'] != 'passed':
            return result('run-affected', 'NEEDS_EVIDENCE', 'Run narrow real checks on current source')
        if s['uat'] == 'pending':
            return result('explore-uat', 'NEEDS_EVIDENCE', 'Demonstrate observable user acceptance with disposable scenarios')
        if s['uat'] == 'not_needed' and (s['risk'] != 'routine' or set(s['changed']) & {'security','persistence','protocol'}):
            return result('explore-uat', 'NEEDS_EVIDENCE', 'High-risk change needs actual acceptance or stronger evidence')
        if s['regression'] != 'decided':
            return result('decide-regression', 'NEEDS_EVIDENCE', 'Promote only the smallest necessary protection')
        return result('finish-feature', 'DONE', 'Feature acceptance and regression decision have been reported as observed')
    if s['intent'] == 'merge':
        if s['merge_checks'] == 'failed':
            return result('classify-failure', 'FAILED', 'Merge checks failed')
        if s['merge_checks'] == 'blocked':
            return result('classify-failure', 'BLOCKED', 'Merge evidence missing')
        if s['merge_checks'] != 'passed':
            return result('run-merge', 'NEEDS_EVIDENCE', 'Run quick risk-based integration gate')
        return result('finish-merge', 'DONE', 'Observed merge checks passed on current basis')
    if s['intent'] == 'integration':
        if s['integration_checks'] in {'failed','blocked'}:
            return result('classify-failure', 'FAILED' if s['integration_checks']=='failed' else 'BLOCKED', 'Repair/revert before release')
        if s['integration_checks'] != 'passed':
            return result('run-integration', 'NEEDS_EVIDENCE', 'Run broad integration and critical consumer paths')
        return result('finish-integration', 'DONE', 'Observed integration checks passed')
    if s['intent'] == 'release':
        if s['artifact'] != 'ready':
            return result('inspect-artifact', 'BLOCKED', 'Release needs a real identified consumable artifact')
        if s['release_checks'] in {'failed','blocked'}:
            return result('classify-failure','FAILED' if s['release_checks']=='failed' else 'BLOCKED','Certification did not pass')
        if s['release_checks'] != 'passed':
            return result('run-release', 'NEEDS_EVIDENCE', 'Test install/upgrade/publication against exact artifact')
        return result('finish-release','DONE','Reported certification passed on exact artifact')
    if s['intent'] == 'audit':
        return result('audit-portfolio','READY','Measure maintenance costs and deduplicate false gates without mutation')
    raise InvalidState('Unreachable intent')


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print('Usage: affordances.py path-to-observed-state.json | -', file=sys.stderr)
        return 2
    try:
        source = sys.stdin.read() if args[0] == '-' else Path(args[0]).read_text(encoding='utf-8')
        print(json.dumps(affordances(json.loads(source)), ensure_ascii=False, indent=2))
    except (InvalidState, OSError, ValueError) as exc:
        print(f'INVALID_STATE: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
