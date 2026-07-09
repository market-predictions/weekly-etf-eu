from __future__ import annotations

import json
from pathlib import Path

CONTRACT = Path('control/ETF_EU_MVP19_FIX_CLIENT_PACKAGE_AND_UCITS_CLOSE_FETCH_V1.md')
ARTIFACT = Path('output/client_surface/etf_eu_mvp19_fix_client_package_and_ucits_close_fetch_20260709_000000.json')
NOTES = Path('output/client_surface/etf_eu_mvp19_fix_client_package_and_ucits_close_fetch_notes_20260709_000000.md')
CLOSE_RUNNER = Path('pricing/build_ucits_close_price_validation_basket_results.py')
CLOSE_VALIDATOR = Path('tools/validate_ucits_close_price_validation_basket_results.py')
PACKAGE_RENDERER = Path('runtime/render_etf_eu_delivery_package.py')
PACKAGE_VALIDATOR = Path('tools/validate_etf_eu_delivery_package_manifest.py')
SENDER = Path('runtime/send_etf_eu_controlled_report.py')
WORKFLOW = Path('.github/workflows/send-weekly-etf-eu-controlled-transport.yml')


def validate() -> dict:
    for path in [CONTRACT, ARTIFACT, NOTES, CLOSE_RUNNER, CLOSE_VALIDATOR, PACKAGE_RENDERER, PACKAGE_VALIDATOR, SENDER, WORKFLOW]:
        assert path.exists(), f'missing {path}'
    data = json.loads(ARTIFACT.read_text(encoding='utf-8'))
    assert data['work_package_id'] == 'ETF-EU-MVP19-FIX'
    assert data['source_work_package'] == 'ETF-EU-MVP19'
    assert data['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert data['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert data['port_behavior_not_us_assumptions'] is True
    assert data['us_assumptions_copied'] is False
    assert data['close_fetch_runner_created'] is True
    assert data['pdf_package_renderer_created'] is True
    assert data['sender_requires_pdf_package'] is True
    assert data['workflow_requires_pdf_package'] is True
    assert data['client_grade_package_ready'] is False
    assert data['resend_performed'] is False
    assert data['delivery_success_closed'] is False
    assert data['receipt_confirmed'] is False
    assert data['completion_claimed'] is False
    assert data['valuation_grade'] is False
    assert data['funding_authority'] is False
    assert data['portfolio_mutation'] is False
    assert data['production_delivery_authority'] is False
    assert data['selected_next_package'] == 'ETF-EU-MVP19-FIX2'
    sender = SENDER.read_text(encoding='utf-8')
    assert '--require-pdf-package' in sender
    assert '--delivery-package-manifest' in sender
    assert 'application", subtype="pdf"' in sender
    workflow = WORKFLOW.read_text(encoding='utf-8')
    assert 'runtime.render_etf_eu_delivery_package' in workflow
    assert 'validate_etf_eu_delivery_package_manifest.py' in workflow
    assert '--require-pdf-package' in workflow
    assert '--delivery-package-manifest' in workflow
    if data['readiness_status'] == 'client_grade_package_ready_for_controlled_resend':
        assert data['selected_next_package'] == 'ETF-EU-MVP20'
        assert data['close_price_validation_basket_results_created'] is True
        assert data['delivery_package_manifest_created'] is True
        assert data['pdf_output_available'] is True
        assert data['client_grade_package_ready'] is True
    else:
        assert data['readiness_status'] == 'client_package_or_price_fetch_hardening_still_required'
        assert data['selected_next_package'] == 'ETF-EU-MVP19-FIX2'
    assert data['selected_next_package'] != 'OPERATOR_ACTION_REQUIRED'
    assert not data['selected_next_package'].startswith('ETF-EU-WP15')
    return {
        'status': 'valid',
        'work_package_id': 'ETF-EU-MVP19-FIX',
        'readiness_status': data['readiness_status'],
        'selected_next_package': data['selected_next_package'],
    }


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
