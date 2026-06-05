from __future__ import annotations

from pathlib import Path

import pytest

from tools.validate_macro_narrative_client_surface import validate

FIXTURE_DIR = Path("fixtures/macro_narrative")


def test_macro_narrative_client_surface_accepts_safe_bilingual_candidate() -> None:
    validate(FIXTURE_DIR / "safe_shadow_candidate_en_nl.json")


@pytest.mark.parametrize(
    "fixture_name",
    [
        "bad_predictive_language.json",
        "bad_shadow_label_leakage.json",
        "bad_dutch_parity.json",
    ],
)
def test_macro_narrative_client_surface_rejects_bad_fixtures(fixture_name: str) -> None:
    with pytest.raises(RuntimeError):
        validate(FIXTURE_DIR / fixture_name)
