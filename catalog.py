"""Deterministic, explicitly heuristic categories and portable catalogue outputs."""
import copy
import json
import re
from pathlib import Path

CATEGORIES = {
 'commerce': ('Comercio electrónico', 'E-commerce', r'woocommerce|ecommerce|e-commerce|checkout|payment|shopping'),
 'forms': ('Formularios', 'Forms', r'\bforms?\b|contact|survey|poll'),
 'seo': ('SEO y analítica', 'SEO & analytics', r'\bseo\b|analytics|sitemap|related.post|redirect'),
 'security': ('Seguridad y acceso', 'Security & access', r'security|login|ssl|captcha|spam|firewall|rest.api'),
 'backup': ('Copias y migración', 'Backup & migration', r'backup|migration|export|import|duplicat'),
 'performance': ('Rendimiento', 'Performance', r'cache|speed|performance|heartbeat|optimi'),
 'media': ('Multimedia', 'Media', r'image|media|gallery|video|audio|upload|slider'),
 'design': ('Diseño y edición', 'Design & editing', r'widget|elementor|css|font|design|block|editor|sticky|menu|logo'),
 'communication': ('Comunicación', 'Communication', r'chat|social|mail|newsletter|facebook|share|sharing'),
 'administration': ('Administración', 'Administration', r'admin|health|debug|maintenance|notice'),
 'other': ('Sin clasificar', 'Unclassified', r'(?!)'),
}

def categories(record):
    text = ' '.join([record['slug'], record.get('name') or '', *record.get('tags', [])]).lower()
    return [key for key, (_, _, rule) in CATEGORIES.items() if re.search(rule, text)] or ['other']

def enrich(snapshot):
    result = copy.deepcopy(snapshot)
    for record in result['plugins']:
        record['categories'] = categories(record)
        record['category_method'] = 'keyword-heuristic-v1; not reviewed'
    return result

def outputs(snapshot):
    from watch import table
    result = {}
    for lang in ('es', 'en'):
        title = 'Categorías' if lang == 'es' else 'Categories'
        lines = [f'# {title}', '', '[Español](CATEGORIES.md) · [English](CATEGORIES.en.md)', '',
                 'Categorías automáticas orientativas / Heuristic categories, not reviewed.', '']
        for key, labels in CATEGORIES.items():
            rows = [r for r in snapshot['plugins'] if key in r['categories']]
            lines.append(f'- [{labels[lang == "en"]} ({len(rows)})](#' + key + ')')
        for key, labels in CATEGORIES.items():
            rows = [r for r in snapshot['plugins'] if key in r['categories']]
            lines += ['', f'<a id="{key}"></a>', f'## {labels[lang == "en"]}', '', table(dict(snapshot, plugins=rows), lang)]
        result['CATEGORIES' + ('.en' if lang == 'en' else '') + '.md'] = '\n'.join(lines) + '\n'
    template = (Path(__file__).parent / 'web/template.html').read_text(encoding='utf-8')
    payload = json.dumps(dict(snapshot, category_labels={k:v[:2] for k,v in CATEGORIES.items()}), ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026').replace('>', '\\u003e')
    result['docs/index.html'] = template.replace('__CATALOG_DATA__', payload)
    return result
