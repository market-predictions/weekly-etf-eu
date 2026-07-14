from __future__ import annotations

from pathlib import Path

from tools.validate_etf_eu_client_surface_clean import validate_surface


def test_clean_dutch_markdown_passes(tmp_path: Path) -> None:
    markdown = tmp_path / "clean.md"
    markdown.write_text(
        "# Weekly ETF EU Review | Nederlands | 2026-07-12\n\n"
        "| Handelslijn | ISIN | Slot | Status |\n"
        "|---|---|---:|---|\n"
        "| SXR8 · Xetra | IE00B5BMR087 | 711.48 | UCITS-handelslijn geverifieerd |\n"
        "| VWCE · Xetra | IE00BK5BQT80 | 166.14 | Handelslijn nog te verifiëren |\n",
        encoding="utf-8",
    )
    result = validate_surface(markdown=markdown, language="nl")
    assert result["client_surface_clean"] is True
    assert result["authority_metadata_absent"] is True
    assert result["raw_status_enums_absent"] is True


def test_internal_authority_metadata_fails(tmp_path: Path) -> None:
    markdown = tmp_path / "blocked.md"
    markdown.write_text(
        "# Weekly ETF EU Review | English Companion | 2026-07-12\n\n"
        "Verified UCITS trading line\n\n"
        "## 8. Authority flags\n\n"
        "send_executed=false\n",
        encoding="utf-8",
    )
    result = validate_surface(markdown=markdown, language="en")
    assert result["client_surface_clean"] is False
    assert result["authority_metadata_visible"] is True
    assert "send_executed=" in result["forbidden_tokens"]
