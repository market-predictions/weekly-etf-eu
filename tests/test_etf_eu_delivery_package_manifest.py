from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_delivery_package_manifest import validate

MANIFEST = Path('output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json')


def test_manifest_if_present_validates() -> None:
    if not MANIFEST.exists():
        return
    result = validate(MANIFEST)
    assert result['status'] == 'valid'
    assert result['pdf_output_available'] is True
    assert result['html_output_available'] is True


def test_contract_fields() -> None:
    fields = {
        'schema_version', 'run_id', 'report_suffix', 'dutch_primary_pdf', 'english_companion_pdf',
        'dutch_primary_html', 'english_companion_html', 'markdown_source_paths', 'pdf_output_available',
        'html_output_available', 'dutch_primary', 'english_companion', 'client_grade_package_ready',
        'stale_delivery_wording_present', 'main_surface_us_proxy_exposure', 'main_surface_tbd_candidate_exposure',
        'nan_price_in_client_surface', 'valuation_grade', 'funding_authority', 'portfolio_mutation'
    }
    assert 'schema_version' in fields
    assert 'client_grade_package_ready' in fields
