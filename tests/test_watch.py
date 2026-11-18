import csv
import io
import json
import tempfile
import unittest
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

import watch

NOW = datetime(2026, 11, 18, 12, tzinfo=timezone.utc)


def raw(slug='fixture', **changes):
    return dict(slug=slug, name='Fixture', version='1.2', active_installs=20000,
                last_updated='2022-11-01 1:05pm GMT', tested='6.0', requires='5.0', requires_php='7.4', **changes)


class MonitorTests(unittest.TestCase):
    def snapshot(self):
        return watch.refresh(['fixture'], request=lambda _: raw(), now=NOW, delay=0)

    def test_live_shape_and_threshold(self):
        result = self.snapshot()
        r = result['plugins'][0]
        self.assertEqual(result['errors'], 0)
        self.assertEqual(r['last_updated'], '2022-11-01T13:05:00Z')
        self.assertEqual(r['maintenance'], 'no_updates_2y')
        self.assertEqual(r['verified_at'], watch.stamp(NOW))
        for days, expected in [(729, 'updated_within_2y'), (730, 'no_updates_2y')]:
            self.assertEqual(watch.classify({'last_updated': watch.stamp(NOW-timedelta(days=days))}, NOW), expected)

    def test_failures_retain_verified_values_and_mark_stale(self):
        before = self.snapshot()
        def fail(_):
            raise urllib.error.URLError('down')
        after = watch.refresh(['fixture'], before, fail, NOW+timedelta(days=1), 0)
        self.assertEqual(after['errors'], 1)
        for key in ['active_installs', 'last_updated', 'directory_status', 'verified_at']:
            self.assertEqual(after['plugins'][0][key], before['plugins'][0][key])
        self.assertNotEqual(after['plugins'][0]['checked_at'], before['plugins'][0]['checked_at'])
        self.assertIn('ERROR', watch.table(after, 'es'))
        self.assertEqual(before['plugins'][0]['check_status'], 'ok')

    def test_first_failure_unknown_not_closed(self):
        result = watch.refresh(['fixture'], request=lambda _: {'error':'Unexpected server response'}, now=NOW, delay=0)
        self.assertEqual(result['plugins'][0]['maintenance'], 'unknown')
        self.assertNotIn('active_installs', result['plugins'][0])

    def test_closed_retains_labeled_historical_installs(self):
        before = self.snapshot()
        closed = {'slug':'fixture','name':'Fixture','closed':True,'error':'closed','closed_date':'2026-11-17','reason_text':'Author Request'}
        after = watch.refresh(['fixture'], before, lambda _: closed, NOW+timedelta(days=1), 0)
        r = after['plugins'][0]
        self.assertEqual(r['directory_status'], 'closed')
        self.assertEqual(r['closure_reason'], 'Author Request')
        self.assertEqual(r['metadata_observed_at'], before['plugins'][0]['metadata_observed_at'])
        self.assertIn('20000+ (hist.)', watch.table(after, 'es'))
        self.assertIn('directory_status', after['changes'][0]['fields'])

    def test_not_found_is_explicit_and_distinct(self):
        result = watch.refresh(['fixture'], self.snapshot(), lambda _: {'error':'Plugin not found.'}, NOW, 0)
        self.assertEqual(result['errors'], 0)
        self.assertEqual(result['plugins'][0]['maintenance'], 'not_found')
        self.assertIn('(hist.)', watch.table(result, 'en'))

    def test_renewed_plugin_and_no_change(self):
        before = self.snapshot()
        same = watch.refresh(['fixture'], before, lambda _: raw(), NOW, 0)
        self.assertEqual(same['changes'], [])
        updated = raw();updated['last_updated'] = '2026-11-17 4:05pm GMT'
        after = watch.refresh(['fixture'], before, lambda _: updated, NOW, 0)
        self.assertEqual(after['plugins'][0]['maintenance'], 'updated_within_2y')
        self.assertEqual(len(after['changes']), 1)

    def test_identity_dates_counts_and_errors_fail_closed(self):
        for change in [{'slug':'other'}, {'active_installs':True}, {'active_installs':-1}, {'active_installs':'20000'}, {'last_updated':'yesterday'}, {'error':'oops'}]:
            with self.subTest(change=change):
                value = raw();value.update(change)
                with self.assertRaises(ValueError):
                    watch.normalize('fixture', value)

    def test_watchlist_strict(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'watchlist.json'
            for slugs in [[], ['../evil'], ['ok','ok'], ['UPPER'], [1], ['a']*501]:
                p.write_text(json.dumps({'plugins':slugs}), encoding='utf-8')
                with self.assertRaises(ValueError):watch.load_watchlist(p)
            p.write_text('{"plugins":["hello-dolly"]}', encoding='utf-8')
            self.assertEqual(watch.load_watchlist(p), ['hello-dolly'])

    def test_untrusted_names_html_markdown_and_csv(self):
        result = self.snapshot();result['plugins'][0]['name'] = '<img src=x onerror=alert(1)>|[link](evil)'
        rendered = watch.table(result, 'es')
        self.assertNotIn('<img', rendered)
        self.assertNotIn('[link]', rendered)
        self.assertIn('&#124;', rendered)
        for value in ['=WEBSERVICE("bad")', ' +cmd', '@SUM(A1)', '-1+2']:
            result['plugins'][0]['name'] = value
            rows = list(csv.DictReader(io.StringIO(watch.csv_export(result))))
            self.assertTrue(rows[0]['name'].startswith("'"))

    def test_publish_validates_markers_before_mutating(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'README.md').write_text('keep', encoding='utf-8')
            with self.assertRaises(ValueError):watch.publish(self.snapshot(), root)
            self.assertFalse((root/'data/plugins.json').exists())
            self.assertEqual((root/'README.md').read_text(), 'keep')

    def test_publish_all_formats_unicode_and_idempotence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ['README.md','README.en.md']:
                (root/name).write_text('Intro\n<!-- WATCH:START -->old<!-- WATCH:END -->\nEnd', encoding='utf-8')
            result = self.snapshot();result['plugins'][0]['name'] = 'Español & 中文'
            watch.publish(result, root)
            first = (root/'README.md').read_bytes()
            watch.publish(result, root)
            self.assertEqual(first, (root/'README.md').read_bytes())
            self.assertEqual(json.loads((root/'data/plugins.json').read_text(encoding='utf-8'))['plugins'][0]['name'], 'Español & 中文')
            self.assertTrue((root/'README.md').read_text(encoding='utf-8').endswith('\nEnd'))
            self.assertEqual(len(list(csv.DictReader(io.StringIO((root/'data/plugins.csv').read_text(encoding='utf-8'))))), 1)

    def test_partial_failure_does_not_erase_other_plugins(self):
        def request(url):
            return raw('first') if 'first' in url else {'error':'other'}
        result = watch.refresh(['first','second'], request=request, now=NOW, delay=0)
        self.assertEqual(result['errors'], 1)
        self.assertEqual(result['plugins'][0]['check_status'], 'ok')
        self.assertEqual(len(result['plugins']), 2)

    def test_discovery_deduplicates_and_filters(self):
        older = raw();recent = raw('recent');recent['last_updated'] = '2026-11-18'
        small = raw('small');small['active_installs'] = 9999
        result = watch.discover(1, lambda _: {'plugins':[older, older, recent, small]}, NOW)
        self.assertEqual([p['slug'] for p in result['candidates']], ['fixture'])

    def test_redirect_and_foreign_host_refused(self):
        self.assertIsNone(watch.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.example'))
        with self.assertRaises(ValueError):watch.fetch('https://evil.example')

    def test_fetch_retries_transient_failures_and_reads_404_json(self):
        class Response(io.BytesIO):
            pass
        opener = unittest.mock.Mock()
        opener.open.side_effect = [urllib.error.HTTPError(watch.API, 503, 'down', {}, None), Response(b'{"error":"Plugin not found."}')]
        with patch('watch.urllib.request.build_opener', return_value=opener), patch('watch.time.sleep'):
            self.assertEqual(watch.fetch(watch.api_url('plugin_information', slug='fixture')), {'error':'Plugin not found.'})
        self.assertEqual(opener.open.call_count, 2)
        opener.open.side_effect = urllib.error.HTTPError(watch.API, 404, 'missing', {}, Response(b'{"error":"Plugin not found."}'))
        with patch('watch.urllib.request.build_opener', return_value=opener):
            self.assertEqual(watch.fetch(watch.api_url('plugin_information', slug='fixture'))['error'], 'Plugin not found.')

    def test_fetch_bounds_and_malformed_json(self):
        for data in [b'x'*(watch.MAX_BYTES+1), b'not json', b'[]']:
            opener = unittest.mock.Mock();opener.open.return_value = io.BytesIO(data)
            with patch('watch.urllib.request.build_opener', return_value=opener):
                with self.assertRaises(ValueError):watch.fetch(watch.api_url('plugin_information', slug='fixture'))


if __name__ == '__main__':
    unittest.main()
