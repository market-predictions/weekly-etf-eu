from pathlib import Path


WORKFLOW = Path('.github/workflows/send-weekly-etf-eu-current-package.yml')


def test_delivery_workflow_normalizes_pasted_input_labels() -> None:
    text = WORKFLOW.read_text(encoding='utf-8')

    assert "s/^[[:space:]]*delivery_mode=//" in text
    assert "s/^[[:space:]]*queue_path=//" in text
    assert "s/^[[:space:]]*send_confirmation=//" in text


def test_send_requires_prepared_locked_queue() -> None:
    text = WORKFLOW.read_text(encoding='utf-8')

    assert 'control/prepared_delivery/*' in text
    assert "grep -q '^accepted_package_lock='" in text
    assert 'ETF_EU_SEND_REQUIRES_PREPARED_DELIVERY_QUEUE' in text
    assert 'ETF_EU_PREPARED_QUEUE_LOCK_REFERENCE_MISSING' in text


def test_default_queue_points_to_accepted_package() -> None:
    text = WORKFLOW.read_text(encoding='utf-8')

    expected = 'control/prepared_delivery/etf_eu_current_package_delivery_request_20260717_141500.md'
    assert text.count(expected) >= 2
