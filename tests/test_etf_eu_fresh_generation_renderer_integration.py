from pathlib import Path

CONTRACT = Path("control/ETF_EU_FRESH_GENERATION_RENDERER_INTEGRATION_CONTRACT_V1.md")


def test_renderer_integration_contract_exists_and_documents_upstream_reuse():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "upstream_pattern_adapted=weekly-etf renderer/package concept" in text
    assert "Dutch primary PDF" in text
    assert "English companion PDF" in text
    assert "send_executed=true" in text
    assert "production_delivery_authority=true" in text


def test_renderer_contract_keeps_generation_and_delivery_separate():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "MVP24 must not dispatch a workflow" in text
    assert "ready_for_controlled_delivery=false" in text
    assert "portfolio_mutation=true" in text
