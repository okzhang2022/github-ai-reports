import datetime as dt
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from report import period, ranking, select_window, compare, render

class ReportTests(unittest.TestCase):
    def test_week_year_boundary(self):
        self.assertEqual(period('weekly', dt.date(2027,1,4)), (dt.date(2026,12,28),dt.date(2027,1,4),'2026-W53'))
    def test_month_leap_year(self):
        self.assertEqual(period('monthly',dt.date(2028,3,1)), (dt.date(2028,2,1),dt.date(2028,3,1),'2028-02'))
    def test_year(self):
        self.assertEqual(period('yearly',dt.date(2027,1,1)), (dt.date(2026,1,1),dt.date(2027,1,1),'2026'))
    def test_new_candidate_has_no_fake_growth(self):
        first={'repos':[{'id':1,'stars':100,'repo':'a/a'}]}
        last={'repos':[{'id':1,'stars':90,'repo':'a/a'},{'id':2,'stars':9000,'repo':'b/b'}]}
        rows=ranking(first,last)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['delta'],-10)
    def test_missing_end_is_failure(self):
        with self.assertRaises(RuntimeError):
            select_window(dt.date(2026,10,19),dt.date(2026,10,26),[{'date':'2026-10-25'}])
    def test_partial_window_explicit(self):
        first,last=select_window(dt.date(2026,10,19),dt.date(2026,10,26),[{'date':'2026-10-24'},{'date':'2026-10-26'}])
        self.assertEqual(first['date'],'2026-10-24')
    def test_coverage_change_blocks_rank_movement(self):
        rows=[{'id':1,'rank':1,'repo':'a/a'}]
        compare(rows,{'complete':True,'coverage_ids':[1,2],'repos':[]},True,[1])
        self.assertEqual(rows[0]['change'],'暂无可比基线')
    def test_valid_comparison(self):
        rows=[{'id':1,'rank':1,'repo':'a/a'},{'id':3,'rank':2,'repo':'c/c'}]
        exits=compare(rows,{'complete':True,'coverage_ids':[1,2,3],'repos':[{'id':1,'rank':2,'repo':'a/a'},{'id':2,'rank':1,'repo':'b/b'}]},True,[1,2,3])
        self.assertEqual(rows[0]['change'],'↑1')
        self.assertEqual(rows[1]['change'],'新上榜')
        self.assertEqual(exits,['b/b'])

if __name__=='__main__': unittest.main()

class IntegrationTests(unittest.TestCase):
    def test_cold_start_outputs_status_instead_of_fake_top_ten(self):
        import tempfile
        import report
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'data/snapshots').mkdir(parents=True)
            (root/'data/reports').mkdir()
            (root/'site').mkdir()
            (root/'templates').mkdir()
            for name in ('style.css','report.js'):
                (root/'templates'/name).write_text((report.ROOT/'templates'/name).read_text())
            report.save(root/'data/snapshots/2026-10-26.json',{'date':'2026-10-26','started_at':'2026-10-26T00:05:00+08:00','finished_at':'2026-10-26T00:06:00+08:00','repos':[{'id':1,'repo':'a/a','stars':200}]})
            with patch.object(report,'ROOT',root):
                result=report.generate('weekly',dt.date(2026,10,26),{})
                self.assertEqual(result['repos'],[])
                self.assertFalse(result['complete'])
                self.assertIn('尚无两个',result['notice'])
                self.assertTrue((root/'site/github-ai-weekly-2026-W43.html').exists())

    def test_unverified_install_command_is_rejected(self):
        import report, os
        from unittest.mock import patch
        detail={k:'text' for k in ['purpose','audience','relevance','priority_reason','demo_goal','requirements','install','demo_input','expected','limits','evidence_quote']}
        detail.update(scenarios=['x'],steps=['x'],priority=True,install='pip install invented-package',evidence_quote='Official example')
        response={'output':[{'content':[{'type':'output_text','text':__import__('json').dumps(detail)}]}]}
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-not-a-real-key'}), patch.object(report,'gh',return_value='Official example'), patch.object(report,'request',return_value=response):
            with self.assertRaisesRegex(RuntimeError,'Installation command'):
                report.enrich([{'repo':'a/a'}],{'model':'test','interests':'test'})

    def test_delivery_receipt_skips_smtp(self):
        import report,tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'data/reports').mkdir(parents=True)
            (root/'data/reports/test.sent').write_text('sent')
            with patch.object(report,'ROOT',root), patch.object(report.smtplib,'SMTP_SSL') as smtp:
                report.notify({'slug':'test'}, {})
                smtp.assert_not_called()
