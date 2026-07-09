from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_PRICING_ARTIFACT = Path('output/pricing/ucits_close_price_validation_basket_results_20260709_000000.json')
DEFAULT_PACKAGE_MANIFEST = Path('output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json')
DEFAULT_NOTES = Path('output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_notes_20260709_000000.md')

REQUIRED_TOP_LEVEL_FIELDS = {
    'schema_version',
    'run_id',
    'generated_at_utc',
    'work_package_id',
    'status',
    'source_work_package',
    'repository_identity',
    'evidence',
    'pricing_summary',
    'package_summary',
    'transport_guard',
    'selected_next_package',
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def validate(
    artifact: Path,
    *,
    pricing_artifact: Path = DEFAULT_PRICING_ARTIFACT,
    package_manifest: Path = DEFAULT_PACKAGE_MANIFEST,
    notes_path: Path = DEFAULT_NOTES,
) -> dict[str, Any]:
    data = _load_json(artifact)
    assert REQUIRED_TOP_LEVEL_FIELDS.issubset(data.keys())
    assert data['schema_version'] == 'etf_eu_mvp19_fix2_ready_for_controlled_resend_v1'
    assert data['work_package_id'] == 'ETF-EU-MVP19-FIX2'
    assert data['status'] == 'completed_client_grade_package_ready_for_controlled_resend'
    assert data['source_work_package'] == 'ETF-EU-MVP19-FIX'
    assert data['selected_next_package'] == 'ETF-EU-MVP20'

    repo = data['repository_identity']
    assert repo['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert repo['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert repo['port_behavior_not_us_assumptions'] is True
    assert repo['us_assumptions_copied'] is False

    evidence = data['evidence']
    assert evidence['ucits_close_price_validation_artifact'] == str(pricing_artifact)
    assert evidence['delivery_package_manifest'] == str(package_manifest)
    for key in [
        'dutch_primary_markdown',
        'english_companion_markdown',
        'dutch_primary_html',
        'dutch_primary_pdf',
        'english_companion_html',
        'english_companion_pdf',
    ]:
        assert evidence[key]
        assert Path(evidence[key]).exists(), f'missing evidence file: {evidence[key]}'

    pricing = data['pricing_summary']
    assert pricing['actual_close_fetch_completed'] is True
    assert pricing['line_count'] == 11
    assert pricing['priced_line_count'] == 10
    assert pricing['failed_line_count'] == 1
    assert pricing['venue_count'] == 3
    assert pricing['currency_count'] == 3
    assert pricing['min_threshold_met'] is True
    assert pricing['batch_stopped_for_rate_limit'] is False
    assert pricing['rate_limit_observed'] is False
    assert pricing['requests_are_serialized'] is True
    assert float(pricing['pause_seconds_between_symbols']) >= 10.0
    assert pricing['rate_limit_mode'] == 'stop'
    assert pricing['valuation_grade'] is False
    assert pricing['funding_authority'] is False
    assert pricing['portfolio_mutation'] is False
    assert pricing['production_delivery_authority'] is False

    package = data['package_summary']
    assert package['client_grade_package_ready'] is True
    assert package['pdf_output_available'] is True
    assert package['html_output_available'] is True
    assert package['dutch_primary'] is True
    assert package['english_companion'] is True
    assert package['main_surface_tbd_candidate_exposure'] is False
    assert package['main_surface_us_proxy_exposure'] is False
    assert package['nan_price_in_client_surface'] is False
    assert package['stale_delivery_wording_present'] is False
    assert package['valuation_grade'] is False
    assert package['funding_authority'] is False
    assert package['portfolio_mutation'] is False

    guard = data['transport_guard']
    assert guard['ready_for_controlled_resend'] is True
    assert guard['resend_performed'] is False
    assert guard['delivery_success_closed'] is False
    assert guard['receipt_confirmed'] is False
    assert guard['completion_claimed'] is False
    assert guard['production_delivery_authority'] is False
    assert guard['explicit_user_instruction_required_before_transport'] is True

    pricing_data = _load_json(pricing_artifact)
    assert pricing_data['line_count'] == pricing['line_count']
    assert pricing_data['priced_line_count'] == pricing['priced_line_count']
    assert pricing_data['failed_line_count'] == pricing['failed_line_count']
    assert pricing_data['venue_count'] == pricing['venue_count']
    assert pricing_data['currency_count'] == pricing['currency_count']
    assert pricing_data['min_threshold_met'] is True
    assert pricing_data['valuation_grade'] is False
    assert pricing_data['funding_authority'] is False
    assert pricing_data['portfolio_mutation'] is False
    assert pricing_data['production_delivery_authority'] is False

    manifest = _load_json(package_manifest)
    assert manifest['client_grade_package_ready'] is True
    assert manifest['pdf_output_available'] is True
    assert manifest['html_output_available'] is True
    assert manifest['dutch_primary'] is True
    assert manifest['english_companion'] is True
    assert manifest['stale_delivery_wording_present'] is False
    assert manifest['main_surface_us_proxy_exposure'] is False
    assert manifest['main_surface_tbd_candidate_exposure'] is False
    assert manifest['nan_price_in_client_surface'] is False
    assert manifest['valuation_grade'] is False
    assert manifest['funding_authority'] is False
    assert manifest['portfolio_mutation'] is False

    assert notes_path.exists(), f'missing closeout notes: {notes_path}'

    return {
        'status': 'valid',
        'artifact': str(artifact),
        'work_package_id': data['work_package_id'],
        'readiness_status': 'client_grade_package_ready_for_controlled_resend',
        'selected_next_package': data['selected_next_package'],
        'client_grade_package_ready': package['client_grade_package_ready'],
        'actual_close_fetch_completed': pricing['actual_close_fetch_completed'],
        'resend_performed': guard['resend_performed'],
        'receipt_confirmed': guard['receipt_confirmed'],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifact', required=True)
    parser.add_argument('--pricing-artifact', default=str(DEFAULT_PRICING_ARTIFACT))
    parser.add_argument('--package-manifest', default=str(DEFAULT_PACKAGE_MANIFEST))
    parser.add_argument('--notes-path', default=str(DEFAULT_NOTES))
    args = parser.parse_args()
    print(json.dumps(
        validate(
            Path(args.artifact),
            pricing_artifact=Path(args.pricing_artifact),
            package_manifest=Path(args.package_manifest),
            notes_path=Path(args.notes_path),
        ),
        indent=2,
    ))


if __name__ == '__main__':
    main()
