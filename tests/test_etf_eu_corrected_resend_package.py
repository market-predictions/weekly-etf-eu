from pathlib import Path

from tools.prepare_etf_eu_corrected_resend_package import _delivery_names
from tools.validate_etf_eu_corrected_resend_package import FORBIDDEN_ORIGINAL_PDFS, REQUIRED_KEYS


ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "tools/prepare_etf_eu_corrected_resend_package.py"
VALIDATOR = ROOT / "tools/validate_etf_eu_corrected_resend_package.py"
RUNNER = ROOT / "runtime/send_etf_eu_current_package_delivery.py"


def test_corrected_delivery_names_are_explicit() -> None:
    names = _delivery_names("260712")
    assert set(names) == REQUIRED_KEYS
    assert names["dutch_primary_pdf"].endswith("_gecorrigeerd.pdf")
    assert names["dutch_primary_html"].endswith("_gecorrigeerd.html")
    assert names["english_companion_pdf"].endswith("_corrected.pdf")
    assert names["english_companion_html"].endswith("_corrected.html")


def test_malformed_original_pdfs_are_forbidden() -> None:
    assert "output/fresh_generation/weekly_etf_eu_review_nl_260712.pdf" in FORBIDDEN_ORIGINAL_PDFS
    assert "output/fresh_generation/weekly_etf_eu_review_260712.pdf" in FORBIDDEN_ORIGINAL_PDFS


def test_package_builder_requires_byte_identity_and_qa() -> None:
    source = PREPARE.read_text(encoding="utf-8")
    assert "shutil.copyfile" in source
    assert "source_sha[label] == delivery_sha[label]" in source
    assert "pdf_client_grade_passed" in source
    assert "visual_review_passed" in source
    assert "corrected_resend_executed\": False" in source


def test_package_validator_recomputes_hashes() -> None:
    source = VALIDATOR.read_text(encoding="utf-8")
    assert "source_actual = _sha256(source)" in source
    assert "destination_actual = _sha256(destination)" in source
    assert "source_actual == destination_actual" in source
    assert "output/corrected_delivery_package" in source


def test_existing_transport_runner_is_reused() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "CORRECTED_QUEUE_SCHEMA" in source
    assert "etf_eu_corrected_transport_result" in source
    assert "etf_eu_corrected_delivery_evidence" in source
    assert "CORRECTION_NOTICE_NL" in source
    assert "original_transport_evidence_overwritten\": False" in source
    assert "receipt_confirmed\": False" in source


def test_authority_boundaries_remain_false() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    for field in (
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
    ):
        assert f'"{field}": False' in source
