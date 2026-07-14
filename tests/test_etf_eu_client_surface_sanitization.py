from __future__ import annotations

from runtime.scrub_etf_eu_client_surface import sanitize_text


def test_dutch_sanitizer_removes_internal_metadata_and_preserves_values() -> None:
    source = """# Weekly ETF EU Review | Nederlands | 2026-07-12

| Trading line | ISIN | Slot | Status |
|---|---|---:|---|
| SXR8 · Xetra | IE00B5BMR087 | 711.48 | verified_ucits_trading_line |
| VWCE · Xetra | IE00BK5BQT80 | 166.14 | candidate_requires_verification |

research candidates blijven niet fundable geworden.

## 8. Authority flags

```text
send_executed=false
valuation_grade=false
```
"""
    cleaned, result = sanitize_text(source, language="nl")

    assert result["client_surface_sanitized"] is True
    assert result["authority_section_removed"] is True
    assert "Authority flags" not in cleaned
    assert "verified_ucits_trading_line" not in cleaned
    assert "candidate_requires_verification" not in cleaned
    assert "UCITS-handelslijn geverifieerd" in cleaned
    assert "Handelslijn nog te verifiëren" in cleaned
    assert "711.48" in cleaned
    assert "166.14" in cleaned
    assert "IE00B5BMR087" in cleaned
    assert "IE00BK5BQT80" in cleaned
    assert "SXR8" in cleaned
    assert "VWCE" in cleaned


def test_english_sanitizer_rejects_unknown_snake_case_status() -> None:
    source = """# Weekly ETF EU Review | English Companion | 2026-07-12

| Trading line | ISIN | Close | Status |
|---|---|---:|---|
| TEST · Xetra | IE00B5BMR087 | 100.00 | unexpected_runtime_enum |
"""
    _cleaned, result = sanitize_text(source, language="en")
    assert result["client_surface_sanitized"] is False
    assert "unexpected_runtime_enum" in result["forbidden_tokens_detected"]
