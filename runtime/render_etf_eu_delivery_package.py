from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

STALE_PATTERNS = [
    'geen e-maillevering uitgevoerd',
    'no email delivery was performed',
    'Productielevering: uitgeschakeld',
    'Production delivery: disabled',
]
US_PROXY_TOKENS = {'SPY', 'SMH', 'GLD', 'PAVE'}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _main_surface(text: str) -> str:
    marker = '## 6.'
    return text.split(marker, 1)[0] if marker in text else text


def _has_stale_wording(*texts: str) -> bool:
    joined = '\n'.join(texts)
    return any(pattern in joined for pattern in STALE_PATTERNS)


def _has_main_proxy_exposure(*texts: str) -> bool:
    main = '\n'.join(_main_surface(text) for text in texts)
    return any(re.search(rf'\b{re.escape(token)}\b', main) for token in US_PROXY_TOKENS)


def _has_main_tbd(*texts: str) -> bool:
    main = '\n'.join(_main_surface(text) for text in texts)
    return bool(re.search(r'\bTBD\b', main))


def _has_nan(*texts: str) -> bool:
    main = '\n'.join(_main_surface(text) for text in texts)
    return bool(re.search(r'\bnan\b', main, re.IGNORECASE))


def markdown_to_html(markdown: str, *, title: str) -> str:
    body: list[str] = []
    in_table = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line:
            if in_table:
                body.append('</tbody></table>')
                in_table = False
            continue
        if line.startswith('|') and line.endswith('|'):
            cells = [html.escape(cell.strip()) for cell in line.strip('|').split('|')]
            if all(set(cell) <= {'-', ':'} for cell in cells):
                continue
            if not in_table:
                body.append('<table><tbody>')
                in_table = True
            body.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>')
            continue
        if in_table:
            body.append('</tbody></table>')
            in_table = False
        if line.startswith('# '):
            body.append(f'<h1>{html.escape(line[2:])}</h1>')
        elif line.startswith('## '):
            body.append(f'<h2>{html.escape(line[3:])}</h2>')
        elif line.startswith('- '):
            body.append(f'<p class="bullet">- {html.escape(line[2:])}</p>')
        elif line.startswith('> '):
            body.append(f'<p class="callout">{html.escape(line[2:])}</p>')
        else:
            body.append(f'<p>{html.escape(line)}</p>')
    if in_table:
        body.append('</tbody></table>')
    css = '''
    body { font-family: Arial, sans-serif; margin: 36px; color: #111827; }
    h1 { font-size: 24px; margin-bottom: 16px; }
    h2 { font-size: 18px; margin-top: 24px; border-bottom: 1px solid #d1d5db; padding-bottom: 4px; }
    p { font-size: 11.5pt; line-height: 1.35; }
    .callout { background: #f3f4f6; padding: 10px; border-left: 4px solid #6b7280; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 10pt; }
    td { border: 1px solid #d1d5db; padding: 6px; vertical-align: top; }
    .bullet { margin-left: 12px; }
    '''
    return '<!doctype html><html><head><meta charset="utf-8"><title>' + html.escape(title) + '</title><style>' + css + '</style></head><body>' + '\n'.join(body) + '</body></html>'


def _pdf_escape(text: str) -> str:
    text = text.encode('latin-1', errors='replace').decode('latin-1')
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def _wrap_lines(text: str, width: int = 92) -> list[str]:
    words = re.sub(r'[#>*`|]', ' ', text).split()
    lines: list[str] = []
    current = ''
    for word in words:
        if len(current) + len(word) + 1 > width:
            if current:
                lines.append(current)
            current = word
        else:
            current = (current + ' ' + word).strip()
    if current:
        lines.append(current)
    return lines


def markdown_to_simple_pdf(markdown: str, path: Path, *, title: str) -> None:
    lines = [title, '']
    for raw in markdown.splitlines():
        if not raw.strip():
            lines.append('')
            continue
        lines.extend(_wrap_lines(raw))
    rendered = []
    y = 780
    rendered.append('BT /F1 10 Tf')
    for line in lines[:95]:
        if y < 40:
            break
        rendered.append(f'72 {y} Td ({_pdf_escape(line)}) Tj')
        rendered.append('0 -13 Td')
        y -= 13
    rendered.append('ET')
    stream = '\n'.join(rendered)
    objects = [
        '1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj',
        '2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj',
        '3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj',
        '4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj',
        f'5 0 obj << /Length {len(stream.encode("latin-1", errors="replace"))} >> stream\n{stream}\nendstream endobj',
    ]
    content = '%PDF-1.4\n'
    offsets = [0]
    for obj in objects:
        offsets.append(len(content.encode('latin-1')))
        content += obj + '\n'
    xref = len(content.encode('latin-1'))
    content += 'xref\n0 6\n0000000000 65535 f \n'
    for offset in offsets[1:]:
        content += f'{offset:010d} 00000 n \n'
    content += f'trailer << /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'
    path.write_bytes(content.encode('latin-1', errors='replace'))


def build_package(*, run_id: str, report_suffix: str, output_dir: Path) -> Path:
    nl_md = Path(f'output/weekly_etf_eu_review_nl_{report_suffix}.md')
    en_md = Path(f'output/weekly_etf_eu_review_{report_suffix}.md')
    output_dir.mkdir(parents=True, exist_ok=True)
    nl_text = _read(nl_md)
    en_text = _read(en_md)
    nl_html = output_dir / f'weekly_etf_eu_review_nl_{report_suffix}.html'
    en_html = output_dir / f'weekly_etf_eu_review_{report_suffix}.html'
    nl_pdf = output_dir / f'weekly_etf_eu_review_nl_{report_suffix}.pdf'
    en_pdf = output_dir / f'weekly_etf_eu_review_{report_suffix}.pdf'
    nl_html.write_text(markdown_to_html(nl_text, title='Weekly ETF EU Review NL'), encoding='utf-8')
    en_html.write_text(markdown_to_html(en_text, title='Weekly ETF EU Review EN'), encoding='utf-8')
    markdown_to_simple_pdf(nl_text, nl_pdf, title='Weekly ETF EU Review NL')
    markdown_to_simple_pdf(en_text, en_pdf, title='Weekly ETF EU Review EN')
    stale = _has_stale_wording(nl_text, en_text)
    proxies = _has_main_proxy_exposure(nl_text, en_text)
    tbd = _has_main_tbd(nl_text, en_text)
    nan = _has_nan(nl_text, en_text)
    client_ready = all([nl_pdf.exists(), en_pdf.exists(), nl_html.exists(), en_html.exists(), not stale, not proxies, not tbd, not nan])
    manifest = {
        'schema_version': 'etf_eu_delivery_package_manifest_v1',
        'run_id': run_id,
        'report_suffix': report_suffix,
        'generated_at_utc': _utc_now(),
        'dutch_primary_pdf': str(nl_pdf),
        'english_companion_pdf': str(en_pdf),
        'dutch_primary_html': str(nl_html),
        'english_companion_html': str(en_html),
        'markdown_source_paths': [str(nl_md), str(en_md)],
        'pdf_output_available': nl_pdf.exists() and en_pdf.exists(),
        'html_output_available': nl_html.exists() and en_html.exists(),
        'dutch_primary': True,
        'english_companion': True,
        'client_grade_package_ready': client_ready,
        'stale_delivery_wording_present': stale,
        'main_surface_us_proxy_exposure': proxies,
        'main_surface_tbd_candidate_exposure': tbd,
        'nan_price_in_client_surface': nan,
        'valuation_grade': False,
        'funding_authority': False,
        'portfolio_mutation': False,
    }
    path = output_dir / f'etf_eu_delivery_package_manifest_{run_id}.json'
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'ETF_EU_DELIVERY_PACKAGE_MANIFEST_OK | manifest={path} | ready={client_ready}')
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--report-suffix', required=True)
    parser.add_argument('--output-dir', default='output/delivery_package')
    args = parser.parse_args()
    build_package(run_id=args.run_id, report_suffix=args.report_suffix, output_dir=Path(args.output_dir))


if __name__ == '__main__':
    main()
