import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('backlog_ready_helper',ROOT/'scripts/ready_candidates.py')
helper = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helper
spec.loader.exec_module(helper)


def payload(tasks):
    return {"schemaVersion": 1, "kind": "task-list", "tasks": tasks}


def task(tid, ready=True, archived=False):
    return {"id": tid, "title": "Task " + tid, "isReady": ready, "archived": archived,
            "status": "To Do", "priority": "High"}


class SnapshotTests(unittest.TestCase):
    def test_preserves_upstream_order_without_reinventing_priority(self):
        tasks=[task('T-12'),task('T-6',False),task('T-2')]
        o=helper.candidates(payload(tasks))
        self.assertEqual([x['id'] for x in o['candidates']],['T-12','T-2'])
        self.assertEqual(o['total_in_snapshot'],3)
        self.assertEqual(o['ready_in_snapshot'],2)

    def test_limits_display_without_losing_total(self):
        o=helper.candidates(payload([task(f'T-{i}') for i in range(10)]),2)
        self.assertEqual(len(o['candidates']),2)
        self.assertEqual(o['ready_in_snapshot'],10)
        self.assertTrue(o['truncated_candidates'])

    def test_empty_snapshot_is_valid_not_an_error(self):
        o=helper.candidates(payload([]))
        self.assertEqual(o['candidates'],[])

    def test_rejects_unexpected_envelope(self):
        for obj in ({'schemaVersion':2,'kind':'task-list','tasks':[]},
                    {'schemaVersion':1,'kind':'task-view','tasks':[]},
                    {'schemaVersion':True,'kind':'task-list','tasks':[]}):
            with self.subTest(obj=obj), self.assertRaises(ValueError):helper.candidates(obj)

    def test_rejects_missing_or_duplicate_id(self):
        for items in ([task('T-1'),task('T-1')],[{'title':'oops','isReady':True,'archived':False}]):
            with self.assertRaises(ValueError):helper.candidates(payload(items))

    def test_requires_authoritative_isready_and_archived(self):
        for item in ({'id':'T-1','title':'X','archived':False},
                     {'id':'T-1','title':'X','isReady':False},
                     {'id':'T-1','title':'X','isReady':1,'archived':False}):
            with self.assertRaises(ValueError):helper.candidates(payload([item]))

    def test_contradictory_archived_ready_fails_closed(self):
        with self.assertRaises(ValueError):helper.candidates(payload([task('T-1',True,True)]))

    def test_rejects_unbounded_limit(self):
        for lim in (0,21,True):
            with self.assertRaises(ValueError):helper.candidates(payload([]),lim)

    def test_source_fixture_is_not_live_application(self):
        f=ROOT/'examples/ready-list.json'
        o=helper.candidates(json.loads(f.read_text()))
        self.assertEqual([x['id'] for x in o['candidates']],['TASK-9','TASK-12'])


if __name__=='__main__': unittest.main()
