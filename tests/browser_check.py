"""Browser regression checks against generated HTML, without a web server."""
import json
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
import catalog
ROOT=Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(accept_downloads=True)
        errors=[];page.on('pageerror',lambda error: errors.append(str(error)))
        page.goto((ROOT/'docs/index.html').as_uri())
        total=page.locator('#data').text_content();total=len(json.loads(total)['plugins'])
        assert page.locator('#rows tr').count()==min(total,50)
        page.locator('#search').fill('health-check')
        assert page.locator('#rows tr').count()==1
        assert 'Health Check' in page.locator('#rows').inner_text()
        page.locator('#category').select_option('commerce')
        assert 'No hay resultados' in page.locator('#rows').inner_text()
        page.locator('#reset').click()
        page.locator('#category').select_option('commerce')
        page.locator('#installs').select_option('10000')
        page.locator('#sort').select_option('1')
        rows=page.evaluate('filtered')
        assert rows and all('commerce' in r['categories'] and r['active_installs']>=10000 for r in rows)
        assert [r['active_installs'] for r in rows]==sorted(r['active_installs'] for r in rows)
        with page.expect_download() as info:page.locator('#csv').click()
        download=info.value
        text=Path(download.path()).read_text(encoding='utf-8-sig')
        import csv,io
        assert len(list(csv.DictReader(io.StringIO(text))))==len(rows)
        page.locator('#language').click()
        assert page.locator('html').get_attribute('lang')=='en'
        assert page.locator('#category').input_value()=='commerce'
        page.locator('#reset').click()
        if total>50:
            first=page.locator('#rows tr').first.inner_text()
            page.locator('#next').click()
            assert page.locator('#rows tr').first.inner_text()!=first
            page.locator('#prev').click()
            assert page.locator('#rows tr').first.inner_text()==first
        for sort in ['0','1','2','3','4']:
            page.locator('#sort').select_option(sort)
            assert len(page.evaluate('filtered'))==total
        page.locator('#age').select_option('1825')
        from datetime import datetime
        for r in page.evaluate('filtered'):
            assert (datetime.fromisoformat(json.loads((ROOT/'data/plugins.json').read_text(encoding='utf-8'))['generated_at'].replace('Z','+00:00'))-datetime.fromisoformat(r['last_updated'].replace('Z','+00:00'))).days>=1825
        page.locator('#age').select_option('0')
        page.locator('#status').select_option('no_updates_2y')
        assert all(r['maintenance']=='no_updates_2y' for r in page.evaluate('filtered'))
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(ROOT.parent/'wp-plugin-watch-explorer-mobile.png'),full_page=True)
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('#reset').click()
        page.screenshot(path=str(ROOT.parent/'wp-plugin-watch-explorer.png'),full_page=False)
        page.locator('#search').fill('no-result-xyz')
        assert 'No results' in page.locator('#rows').inner_text()
        # Inject hostile source metadata into a separately rendered file.
        snapshot=json.loads((ROOT/'data/plugins.json').read_text(encoding='utf-8'))
        snapshot['plugins']=snapshot['plugins'][:1]
        snapshot['plugins'][0]['name']='</script><img src=x onerror="window.PWNED=1">'
        snapshot['plugins'][0]['check_status']='error'
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'hostile.html';path.write_text(catalog.outputs(catalog.enrich(snapshot))['docs/index.html'],encoding='utf-8')
            page.goto(path.as_uri())
            assert page.locator('#rows img').count()==0
            assert page.evaluate('window.PWNED') is None
            page.locator('#status').select_option('error')
            assert page.locator('#rows tr').count()==1
            assert 'Error de consulta' in page.locator('#rows').inner_text()
        assert not errors,errors
        browser.close()
        print(f'Browser checks passed: {total} live records; search, combined filters, sorting, pagination, CSV, language, mobile, errors, XSS.')

if __name__=='__main__':main()
