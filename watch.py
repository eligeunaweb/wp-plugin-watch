"""A small, dependency-free WordPress.org maintenance monitor (Python 3.11+)."""
import argparse
import csv
import html
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = 'https://api.wordpress.org/plugins/info/1.2/'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
MAX_BYTES = 8 * 1024 * 1024
FIELDS = ('name', 'version', 'active_installs', 'last_updated', 'tested', 'requires', 'requires_php', 'directory_status', 'closed_date', 'closure_reason')


def utc_now():
    return datetime.now(timezone.utc)


def stamp(now):
    return now.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def parse_date(value):
    if not isinstance(value, str):
        raise ValueError('missing date')
    for fmt in ('%Y-%m-%d %I:%M%p GMT', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def api_url(action, **args):
    params = {'action': action, **{f'request[{k}]': v for k, v in args.items()}}
    params.update({f'request[fields][{k}]': '0' for k in ('sections', 'description', 'short_description', 'banners', 'icons', 'screenshots', 'reviews', 'contributors', 'ratings')})
    params['request[fields][active_installs]'] = '1'
    return API + '?' + urllib.parse.urlencode(params)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url):
    if not url.startswith(API + '?'):
        raise ValueError('unapproved API URL')
    request = urllib.request.Request(url, headers={'User-Agent': 'wp-plugin-watch/1.0 (public maintenance research)', 'Accept': 'application/json'})
    opener = urllib.request.build_opener(NoRedirect())
    for attempt in range(3):
        try:
            try:
                response = opener.open(request, timeout=20)
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise
                response = error
            with response:
                raw = response.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise ValueError('response too large')
                data = json.loads(raw.decode('utf-8'))
                if not isinstance(data, dict):
                    raise ValueError('invalid API object')
                return data
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if isinstance(error, urllib.error.HTTPError) and error.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def short_text(value, limit=300):
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError('invalid metadata text')
    return html.unescape(value)


def normalize(slug, raw):
    if not isinstance(raw, dict):
        raise ValueError('invalid API record')
    if raw.get('error') == 'Plugin not found.':
        return {'directory_status': 'not_found'}
    if raw.get('slug') != slug:
        raise ValueError('plugin identity mismatch')
    if raw.get('closed') is True and raw.get('error') == 'closed':
        date = short_text(raw.get('closed_date'))
        if date:
            parse_date(date)
        return {'name': short_text(raw.get('name')), 'directory_status': 'closed', 'closed_date': date,
                'closure_reason': short_text(raw.get('reason_text') or raw.get('reason') or None)}
    if 'error' in raw:
        raise ValueError('unrecognized API error')
    installs = raw.get('active_installs')
    if type(installs) is not int or installs < 0:
        raise ValueError('invalid installation count')
    updated = stamp(parse_date(raw.get('last_updated')))
    tags = raw.get('tags', {})
    if not isinstance(tags, dict) or len(tags) > 100 or any(not isinstance(t, str) for t in tags.values()):
        raise ValueError('invalid tags')
    return {'tags': [short_text(t) for t in tags.values()], 'name': short_text(raw.get('name')), 'version': short_text(raw.get('version')),
            'active_installs': installs, 'last_updated': updated,
            'tested': short_text(raw.get('tested')), 'requires': short_text(raw.get('requires')),
            'requires_php': short_text(raw.get('requires_php')), 'directory_status': 'open',
            'closed_date': None, 'closure_reason': None}


def classify(record, now, threshold=730):
    if record.get('directory_status') == 'closed':
        return 'closed'
    if record.get('directory_status') == 'not_found':
        return 'not_found'
    if not record.get('last_updated'):
        return 'unknown'
    return 'no_updates_2y' if (now - parse_date(record['last_updated'])).days >= threshold else 'updated_within_2y'


def refresh(slugs, previous=None, request=fetch, now=None, delay=1):
    now = now or utc_now()
    old = {r['slug']: r for r in (previous or {}).get('plugins', [])}
    records, changes = [], []
    for index, slug in enumerate(slugs):
        before = old.get(slug, {})
        record = dict(before)
        record.update(slug=slug, source=api_url('plugin_information', slug=slug), checked_at=stamp(now))
        try:
            metadata = normalize(slug, request(record['source']))
            record.update(metadata)
            record.update(check_status='ok', verified_at=stamp(now), error=None)
            # A closed/not-found API response does not supply current install counts.
            if metadata['directory_status'] == 'open':
                record['metadata_observed_at'] = stamp(now)
            record['maintenance'] = classify(record, now)
            differences = {k: {'before': before.get(k), 'after': record.get(k)} for k in FIELDS if before and before.get(k) != record.get(k)}
            if differences:
                changes.append({'slug': slug, 'at': stamp(now), 'fields': differences})
        except (ValueError, TypeError, KeyError, urllib.error.URLError, TimeoutError, OSError):
            record.update(check_status='error', error='Source unavailable or invalid response; last valid metadata retained.')
            record.setdefault('maintenance', 'unknown')
        records.append(record)
        if delay and index < len(slugs) - 1:
            time.sleep(delay)
    return {'schema_version': 1, 'generated_at': stamp(now), 'coverage': 'Explicit watchlist, not the entire WordPress directory.',
            'plugins': records, 'changes': changes, 'errors': sum(r['check_status'] == 'error' for r in records)}


def load_watchlist(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    slugs = value.get('plugins')
    if not isinstance(slugs, list) or not 1 <= len(slugs) <= 500 or any(not isinstance(s, str) or not SLUG.fullmatch(s) for s in slugs) or len(set(slugs)) != len(slugs):
        raise ValueError('watchlist must contain 1..500 distinct plugin slugs')
    return slugs


def safe_cell(value):
    return html.escape(str(value if value is not None else '—')).replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ').replace('`', '&#96;').replace('[', '&#91;').replace(']', '&#93;')


LABELS = {'es': {'closed': 'Cerrado', 'not_found': 'No encontrado', 'no_updates_2y': 'Sin actualizar ≥730 días', 'updated_within_2y': 'Actualizado hace <730 días', 'unknown': 'Sin datos'},
          'en': {'closed': 'Closed', 'not_found': 'Not found', 'no_updates_2y': 'No updates ≥730 days', 'updated_within_2y': 'Updated within 730 days', 'unknown': 'Unknown'}}


def table(snapshot, lang):
    es = lang == 'es'
    rows = [f"{'Última consulta' if es else 'Last run'}: **{snapshot['generated_at']}** · {'Errores' if es else 'Errors'}: **{snapshot['errors']}**",
            '', '| Plugin | ' + ('Instalaciones¹ | Última actualización | WP probado² | Estado³ | Consulta |' if es else 'Installs¹ | Last updated | WP tested² | Status³ | Check |'),
            '|---|---:|---|---|---|---|']
    for r in sorted(snapshot['plugins'], key=lambda r: (-(r.get('active_installs') or 0), r['slug'])):
        installs = str(r['active_installs']) + '+' if r.get('active_installs') is not None else '—'
        if r.get('directory_status') in ('closed', 'not_found') and r.get('active_installs') is not None:
            installs += ' (hist.)'
        status = LABELS[lang][r.get('maintenance', 'unknown')]
        checked = ('ERROR; dato anterior' if es else 'ERROR; previous data') if r['check_status'] == 'error' else 'OK'
        rows.append(f"| [{safe_cell(r.get('name') or r['slug'])}](https://wordpress.org/plugins/{r['slug']}/) | {installs} | {safe_cell(r.get('last_updated'))} | {safe_cell(r.get('tested'))} | {status} | {checked} |")
    rows += ['', ('¹ Cifras publicadas por WordPress.org, no conteos exactos. Hist.: último valor conocido, no actual.\n² Declaración del autor; no hemos probado esa compatibilidad.\n³ Antigüedad o cierre no demuestran una vulnerabilidad. No es una lista de plugins «inseguros».' if es else '¹ WordPress.org published figures, not exact counts. Hist.: last known value, not current.\n² Author declaration; compatibility has not been tested here.\n³ Age or closure does not establish a vulnerability. This is not an “unsafe plugins” list.'), '',
             ('Datos completos, fechas de verificación y motivos públicos de cierre: [JSON](data/plugins.json) · [CSV](data/plugins.csv).' if es else 'Full metadata, verification dates and public closure reasons: [JSON](data/plugins.json) · [CSV](data/plugins.csv).')]
    return '\n'.join(rows)


def csv_export(snapshot):
    out = io.StringIO(newline='')
    fields = ['slug', 'categories', 'category_method', *FIELDS, 'maintenance', 'check_status', 'checked_at', 'verified_at', 'metadata_observed_at', 'source']
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for record in snapshot['plugins']:
        row = {k: record.get(k, '') for k in fields}
        row['categories'] = ';'.join(record.get('categories', []))
        for k, v in row.items():
            if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')):
                row[k] = "'" + v
        writer.writerow(row)
    return out.getvalue()


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(text, encoding='utf-8', newline='\n')
    os.replace(temp, path)


def publish(snapshot, root=ROOT):
    from catalog import enrich, outputs
    snapshot = enrich(snapshot)
    generated = {root / 'data/plugins.json': json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n',
                 root / 'data/plugins.csv': csv_export(snapshot)}
    for lang, filename in [('en', 'README.md'), ('es', 'README.es.md')]:
        path = root / filename
        source = path.read_text(encoding='utf-8')
        start, end = '<!-- WATCH:START -->', '<!-- WATCH:END -->'
        if source.count(start) != 1 or source.count(end) != 1 or source.index(start) > source.index(end):
            raise ValueError('README markers missing or ambiguous')
        generated[path] = source.split(start)[0] + start + '\n\n' + table(snapshot, lang) + '\n\n' + end + source.split(end)[1]
    generated.update({root / name: content for name, content in outputs(snapshot).items()})
    # All render/validation work completes before any destination is changed.
    for path, content in generated.items():
        atomic_write(path, content)


def discover(pages, request=fetch, now=None, min_installs=10000):
    now = now or utc_now()
    found = {}
    for page in range(1, pages + 1):
        response = request(api_url('query_plugins', browse='popular', per_page=250, page=page))
        for raw in response['plugins']:
            slug = raw.get('slug', '')
            if not SLUG.fullmatch(slug):
                continue
            try:
                row = normalize(slug, raw)
            except (ValueError, TypeError):
                continue
            if row.get('active_installs', 0) >= min_installs and classify(row, now) == 'no_updates_2y':
                found[slug] = {'slug': slug, **row}
        if page < pages:
            time.sleep(1)
    return {'discovered_at': stamp(now), 'pages_queried': pages, 'min_installs': min_installs, 'method': f'Popular endpoint; 250 per page; >={min_installs} published installs; >=730 days without updates. Sample only; closed plugins may not appear.',
            'candidates': sorted(found.values(), key=lambda r: (-r['active_installs'], r['slug']))}


def expanded_slugs(existing, candidates, limit=500):
    """Keep tracked records and add eligible candidates in their ranked order."""
    return list(dict.fromkeys(existing + [r['slug'] for r in candidates]))[:limit]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['refresh', 'discover', 'expand', 'render'])
    parser.add_argument('--pages', type=int, default=20)
    parser.add_argument('--min-installs', type=int, default=1000)
    args = parser.parse_args()
    if args.command in ('discover', 'expand'):
        if args.min_installs < 1:
            parser.error('min-installs must be positive')
        if not 1 <= args.pages <= 20:
            parser.error('pages must be 1..20')
        result = discover(args.pages, min_installs=args.min_installs)
        atomic_write(ROOT / 'data/candidates.json', json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        if args.command == 'expand':
            path = ROOT / 'watchlist.json'
            config = json.loads(path.read_text(encoding='utf-8'))
            slugs = load_watchlist(path)
            config['plugins'] = expanded_slugs(slugs, result['candidates'])
            atomic_write(path, json.dumps(config, indent=2) + '\n')
        print(f"Found {len(result['candidates'])} candidates.")
        return 0
    slugs = load_watchlist(ROOT / 'watchlist.json')
    previous_path = ROOT / 'data/plugins.json'
    previous = json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else None
    if previous is not None and previous.get('schema_version') != 1:
        raise ValueError('unsupported saved schema')
    if args.command == 'render' and previous is None:
        parser.error('render requires an existing data/plugins.json snapshot')
    result = previous if args.command == 'render' else refresh(slugs, previous)
    publish(result)
    print(f"Snapshot: {len(result['plugins'])} plugins; {result['errors']} errors; {len(result['changes'])} metadata changes.")
    return 1 if result['errors'] and args.command == 'refresh' else 0


if __name__ == '__main__':
    raise SystemExit(main())
