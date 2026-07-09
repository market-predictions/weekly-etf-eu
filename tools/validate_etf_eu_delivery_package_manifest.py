from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['schema_version'] == 'etf_eu_delivery_package_manifest_v1'
    assert data['dutch_primary'] is True
    assert data['english_companion'] is True
    assert data['valuation_grade'] is False
    assert data['funding_authority'] is False
    assert data['portfolio_mutation'] is False
    for key in ['dutch_primary_pdf', 'english_companion_pdf', 'dutch_primary_html', 'english_companion_html']:
        assert data[key]
        assert Path(data[key]).exists(), f'missing package asset {data[key]}'
    assert data['pdf_output_available'] is True
    assert data['html_output_available'] is True
    if data['client_grade_package_ready'] is True:
        assert data['stale_delivery_wording_present'] is False
        assert data['main_surface_us_proxy_exposure'] is False
        assert data['main_surface_tbd_candidate_exposure'] is False
        assert data['nan_price_in_client_surface'] is False
    return {
        'status': 'valid',
        'manifest': str(path),
        'pdf_output_available': data['pdf_output_available'],
        'html_output_available': data['html_output_available'],
        'client_grade_package_ready': data['client_grade_package_ready'],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.manifest)), indent=2))


if __name__ == '__main__':
    main()
