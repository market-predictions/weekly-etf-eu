import pytest

from pricing.price_result_schema import ALLOWED_AUTHORITY_TIERS, ALLOWED_LICENSE_CLASSES
from pricing.source_metadata_policy import (
    DEFAULT_SOURCE_METADATA,
    POLICY_MODE_DIAGNOSTIC_EVIDENCE,
    POLICY_MODE_MARKET_CLOSE_AGREEMENT_CANDIDATES,
    POLICY_MODE_REFERENCE_EVIDENCE,
    POLICY_MODE_VALUATION_CANDIDATE_EVIDENCE,
    REVIEW_STATUS_REVIEWED,
    SOURCE_TYPE_EXCHANGE,
    USAGE_MODE_OFFICIAL_CLOSE,
    SourceMetadata,
    filter_sources_by_policy_mode,
    metadata_by_source_id,
)


def test_default_metadata_source_ids_are_unique():
    indexed = metadata_by_source_id(DEFAULT_SOURCE_METADATA)

    assert len(indexed) == len(DEFAULT_SOURCE_METADATA)
    assert "yahoo_yfinance" in indexed
    assert "issuer_nav" in indexed


def test_default_metadata_aligns_with_price_result_schema_categories():
    for row in DEFAULT_SOURCE_METADATA:
        assert row.license_class in ALLOWED_LICENSE_CLASSES
        assert row.authority_tier in ALLOWED_AUTHORITY_TIERS


def test_market_close_agreement_candidates_exclude_fallback_and_reference_sources():
    rows = filter_sources_by_policy_mode(
        DEFAULT_SOURCE_METADATA,
        policy_mode=POLICY_MODE_MARKET_CLOSE_AGREEMENT_CANDIDATES,
    )
    source_ids = {row.source_id for row in rows}

    assert "euronext_live" in source_ids
    assert "deutsche_boerse_live" in source_ids
    assert "yahoo_yfinance" not in source_ids
    assert "issuer_nav" not in source_ids
    assert all(row.counts_for_market_close_agreement for row in rows)


def test_valuation_candidate_evidence_is_metadata_only_not_authority_promotion():
    rows = filter_sources_by_policy_mode(
        DEFAULT_SOURCE_METADATA,
        policy_mode=POLICY_MODE_VALUATION_CANDIDATE_EVIDENCE,
    )

    assert {row.source_id for row in rows} == {"euronext_live", "deutsche_boerse_live"}
    assert all(row.valuation_candidate_eligible for row in rows)


def test_reference_evidence_returns_issuer_reference_sources_only():
    rows = filter_sources_by_policy_mode(
        DEFAULT_SOURCE_METADATA,
        policy_mode=POLICY_MODE_REFERENCE_EVIDENCE,
    )
    source_ids = {row.source_id for row in rows}

    assert source_ids == {"issuer_nav", "blackrock_issuer_reference", "issuer_factsheet"}
    assert all(not row.counts_for_market_close_agreement for row in rows)


def test_diagnostic_evidence_preserves_input_order_and_includes_all_metadata():
    rows = filter_sources_by_policy_mode(
        DEFAULT_SOURCE_METADATA,
        policy_mode=POLICY_MODE_DIAGNOSTIC_EVIDENCE,
    )

    assert rows == DEFAULT_SOURCE_METADATA


def test_unknown_policy_mode_fails_closed():
    with pytest.raises(ValueError, match="unsupported policy_mode"):
        filter_sources_by_policy_mode(DEFAULT_SOURCE_METADATA, policy_mode="production_delivery")


def test_duplicate_source_ids_fail_closed():
    source = SourceMetadata(
        source_id="duplicate",
        provider_name="Duplicate",
        source_type=SOURCE_TYPE_EXCHANGE,
        usage_mode=USAGE_MODE_OFFICIAL_CLOSE,
        license_class="exchange_public",
        authority_tier="exchange_official",
        review_status=REVIEW_STATUS_REVIEWED,
    )

    with pytest.raises(ValueError, match="duplicate source metadata"):
        metadata_by_source_id((source, source))


def test_reference_source_cannot_count_for_market_close_agreement():
    with pytest.raises(ValueError, match="reference/stale-check sources cannot count"):
        SourceMetadata(
            source_id="bad_reference",
            provider_name="Bad Reference",
            source_type="issuer",
            usage_mode="reference_stale_check",
            license_class="issuer_public",
            authority_tier="diagnostic_candidate_source",
            review_status="reference_only",
            counts_for_market_close_agreement=True,
        )
