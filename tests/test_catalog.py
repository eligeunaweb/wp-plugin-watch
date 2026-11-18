import json
import tempfile
import unittest
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
import catalog
import watch
from test_watch import raw, NOW

class CatalogueTests(unittest.TestCase):
    def test_categories_are_multi_label_and_unclassified(self):
        self.assertEqual(catalog.categories({'slug':'hello-planet','tags':[]}), ['other'])
        result=catalog.categories({'slug':'woocommerce-contact-form','tags':[]})
        self.assertIn('commerce', result)
        self.assertIn('forms', result)

    def test_enrichment_does_not_mutate_source(self):
        original=watch.refresh(['fixture'], request=lambda _:raw(), now=NOW, delay=0)
        result=catalog.enrich(original)
        self.assertNotIn('categories',original['plugins'][0])
        self.assertEqual(result['plugins'][0]['category_method'],'keyword-heuristic-v1; not reviewed')

    def test_html_payload_cannot_close_script(self):
        original=watch.refresh(['fixture'], request=lambda _:raw(), now=NOW, delay=0)
        original['plugins'][0]['name']='</script><script>alert(1)</script>&'
        outputs=catalog.outputs(catalog.enrich(original))
        rendered=outputs['docs/index.html']
        payload=rendered.split('<script type="application/json" id="data">')[1].split('</script>')[0]
        self.assertNotIn('<',payload)
        self.assertEqual(json.loads(payload)['plugins'][0]['name'],original['plugins'][0]['name'])
        self.assertIn('## Sin clasificar',outputs['CATEGORIES.md'])
        self.assertIn('## Unclassified',outputs['CATEGORIES.en.md'])

    def test_discovery_threshold_is_configurable(self):
        item=raw();item['active_installs']=1000
        self.assertEqual(len(watch.discover(1,lambda _:{'plugins':[item]},NOW,1000)['candidates']),1)
        self.assertEqual(len(watch.discover(1,lambda _:{'plugins':[item]},NOW,1001)['candidates']),0)

    def test_tags_are_validated_and_requested(self):
        self.assertNotIn('fields%5D%5Btags%5D=0',watch.api_url('query_plugins'))
        item=raw(tags={'backup':'Backup'})
        self.assertEqual(watch.normalize('fixture',item)['tags'],['Backup'])
        for value in [['wrong'], {'bad':123}]:
            item['tags']=value
            with self.assertRaises(ValueError):watch.normalize('fixture',item)

    def test_expansion_preserves_existing_deduplicates_and_caps(self):
        self.assertEqual(watch.expanded_slugs(['retained','old'], [{'slug':'old'},{'slug':'new'},{'slug':'extra'}], 3), ['retained','old','new'])

    def test_temporary_closure_with_unpublished_reason(self):
        record = watch.normalize('fixture', {'slug':'fixture','name':'Fixture','closed':True,'error':'closed','closed_date':'2026-11-18','reason':False,'reason_text':False})
        self.assertEqual(record['directory_status'], 'closed')
        self.assertIsNone(record['closure_reason'])

    def test_categories_in_csv(self):
        result=catalog.enrich(watch.refresh(['woocommerce-form'],request=lambda _:raw('woocommerce-form'),now=NOW,delay=0))
        self.assertIn('commerce;forms',watch.csv_export(result))
