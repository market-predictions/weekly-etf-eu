from __future__ import annotations

import json
from pathlib import Path

A = Path('output/client_surface/etf_eu_mvp16_guarded_dry_run_verification_20260708_000000.json')
C = Path('control/ETF_EU_MVP16_GUARDED_DRY_RUN_VERIFICATION_V1.md')
N = Path('output/client_surface/etf_eu_mvp16_guarded_dry_run_verification_notes_20260708_000000.md')


def validate() -> dict:
    assert A.exists()
    assert C.exists()
    assert N.exists()
    d = json.loads(A.read_text(encoding='utf-8'))
    assert d['work_package_id'] == 'ETF-EU-MVP16'
    assert d['source_work_package'] == 'ETF-EU-MVP15-FIX'
    assert d['workflow_run_id'] == '28976148251'
    assert d['workflow_conclusion'] == 'success'
    assert d['requested_mode'] == 'dry_run'
    assert d['selected_next_package'] == 'ETF-EU-MVP17'
    assert d['us_assumptions_copied'] is False
    return {'status': 'valid', 'work_package_id': d['work_package_id'], 'selected_next_package': d['selected_next_package']}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
