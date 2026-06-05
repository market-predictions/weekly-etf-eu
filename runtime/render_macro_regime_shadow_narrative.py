from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "macro_regime_shadow_narrative_v1"
DEFAULT_OUTPUT_DIR = Path("output/macro/shadow_narrative")

AUTHORITY_FALSE_FLAGS = {
    "client_facing": False,
    "production_report": False,
    "portfolio_action_authority": False,
    "lane_scoring_authority": False,
    "fundability_authority": False,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_text_if_available(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _read_json_if_available(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _clean(value: Any, default: str = "not_available") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _first_present(payload: dict[str, Any], keys: tuple[str, ...], default: str = "not_available") -> str:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return _clean(payload[key], default)
    return default


def _extract_current_macro_narrative(report_text: str, *, language: str) -> dict[str, str]:
    headings = (
        ("## Macro narrative", "## Deterministic macro narrative", "## Regime Dashboard", "## Macro regime"),
        ("## Macro-narratief", "## Deterministisch macro-narratief", "## Regime-dashboard", "## Macroregime"),
    )
    candidates = headings[1] if language == "nl" else headings[0]

    lines = report_text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() in candidates:
            section_lines: list[str] = [line]
            for later_line in lines[index + 1 :]:
                if later_line.startswith("## "):
                    break
                section_lines.append(later_line)
            text = "\n".join(section_lines).strip()
            return {
                "status": "found",
                "language": language,
                "text": text,
            }

    return {
        "status": "not_found",
        "language": language,
        "text": "No current macro narrative section was found in the supplied report.",
    }


def _normalise_regime_payload(payload: dict[str, Any]) -> dict[str, Any]:
    nested = payload.get("macro_regime")
    if isinstance(nested, dict):
        merged = dict(payload)
        merged.update(nested)
        return merged
    return dict(payload)


def _evidence_lines(payload: dict[str, Any], *, language: str) -> list[str]:
    evidence = (
        payload.get("deterministic_evidence")
        or payload.get("evidence")
        or payload.get("signals")
        or payload.get("components")
        or {}
    )

    if isinstance(evidence, list):
        cleaned = [_clean(item, "not_available") for item in evidence if _clean(item, "")]
    elif isinstance(evidence, dict):
        cleaned = [f"{key}={_clean(value)}" for key, value in sorted(evidence.items())]
    else:
        cleaned = []

    if not cleaned:
        if language == "nl":
            return ["- Geen deterministische bewijsregels meegeleverd; kandidaat blijft beschrijvend en shadow-only."]
        return ["- No deterministic evidence rows supplied; candidate remains descriptive and shadow-only."]

    return [f"- {item}" for item in cleaned]


def build_candidate_narrative(macro_regime_payload: dict[str, Any], *, language: str) -> str:
    payload = _normalise_regime_payload(macro_regime_payload)

    regime = _first_present(
        payload,
        ("deterministic_regime", "regime", "regime_label", "macro_regime_label", "risk_regime"),
        "unclassified",
    )
    confidence = _first_present(payload, ("confidence", "confidence_level", "regime_confidence"), "not_available")
    trend = _first_present(payload, ("trend", "market_trend", "trend_state"), "not_available")
    breadth = _first_present(payload, ("breadth", "market_breadth", "breadth_state"), "not_available")
    credit = _first_present(payload, ("credit", "credit_state", "credit_conditions"), "not_available")
    volatility = _first_present(payload, ("volatility", "volatility_state", "vix_state"), "not_available")
    liquidity = _first_present(payload, ("liquidity", "liquidity_state"), "not_available")
    policy = _first_present(payload, ("policy", "central_bank_policy", "rates_policy"), "not_available")

    evidence = "\n".join(_evidence_lines(payload, language=language))

    if language == "nl":
        return (
            "## Deterministisch macroregime — shadow-kandidaat\n\n"
            "> **SHADOW-ONLY:** Deze tekst is geen client-facing rapporttekst, geen productieoutput, "
            "geen portefeuille-actie, geen lane-score en geen fundability-beslissing.\n\n"
            f"Het deterministische macroregime staat op **{regime}** met confidence **{confidence}**. "
            f"De regelset leest trend={trend}, breedte={breadth}, krediet={credit}, volatiliteit={volatility}, "
            f"liquiditeit={liquidity} en beleidscontext={policy}. Deze kandidaattekst mag alleen worden "
            "vergeleken met het huidige macro-narratief en mag niet automatisch in de productiebrief worden opgenomen.\n\n"
            "### Deterministische bewijsregels\n\n"
            f"{evidence}\n\n"
            "### Autoriteitsgrens\n\n"
            "client_facing=false; production_report=false; portfolio_action_authority=false; "
            "lane_scoring_authority=false; fundability_authority=false."
        )

    return (
        "## Deterministic macro regime — shadow candidate\n\n"
        "> **SHADOW-ONLY:** This text is not client-facing report text, not production output, "
        "not a portfolio action, not a lane score and not a fundability decision.\n\n"
        f"The deterministic macro regime is **{regime}** with confidence **{confidence}**. "
        f"The rule set reads trend={trend}, breadth={breadth}, credit={credit}, volatility={volatility}, "
        f"liquidity={liquidity} and policy context={policy}. This candidate text may only be compared "
        "against the current macro narrative and must not be automatically inserted into the production report.\n\n"
        "### Deterministic evidence rows\n\n"
        f"{evidence}\n\n"
        "### Authority boundary\n\n"
        "client_facing=false; production_report=false; portfolio_action_authority=false; "
        "lane_scoring_authority=false; fundability_authority=false."
    )


def _comparison_markdown(
    *,
    current_en: dict[str, str],
    current_nl: dict[str, str],
    candidate_en: str,
    candidate_nl: str,
) -> str:
    return (
        "# Macro regime shadow narrative comparison\n\n"
        "> **SHADOW-ONLY / NIET VOOR PRODUCTIE:** This artifact compares current report wording with a "
        "deterministic macro regime narrative candidate. It does not modify the production report.\n\n"
        "## Authority flags\n\n"
        "- client_facing=false\n"
        "- production_report=false\n"
        "- portfolio_action_authority=false\n"
        "- lane_scoring_authority=false\n"
        "- fundability_authority=false\n\n"
        "## Current macro narrative — English\n\n"
        f"Status: {current_en['status']}\n\n"
        f"{current_en['text']}\n\n"
        "## Deterministic regime shadow narrative candidate — English\n\n"
        f"{candidate_en}\n\n"
        "## Current macro narrative — Dutch\n\n"
        f"Status: {current_nl['status']}\n\n"
        f"{current_nl['text']}\n\n"
        "## Deterministisch regime shadow-narratief kandidaat — Nederlands\n\n"
        f"{candidate_nl}\n"
    )


def build_macro_regime_shadow_narrative(
    *,
    run_id: str,
    report_date: str,
    current_report_en_text: str = "",
    current_report_nl_text: str = "",
    macro_regime_payload: dict[str, Any] | None = None,
    current_report_en_path: str | None = None,
    current_report_nl_path: str | None = None,
    macro_regime_artifact_path: str | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    payload = macro_regime_payload or {}

    current_en = _extract_current_macro_narrative(current_report_en_text, language="en")
    current_nl = _extract_current_macro_narrative(current_report_nl_text, language="nl")
    candidate_en = build_candidate_narrative(payload, language="en")
    candidate_nl = build_candidate_narrative(payload, language="nl")

    blockers = [
        "shadow-only comparison artifact",
        "client_facing=false",
        "production_report=false",
        "portfolio_action_authority=false",
        "lane_scoring_authority=false",
        "fundability_authority=false",
        "no production report mutation",
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": created_at_utc or _utc_now(),
        "report_date": report_date,
        "status": "shadow_candidate_only",
        "shadow_only": True,
        **AUTHORITY_FALSE_FLAGS,
        "authority": dict(AUTHORITY_FALSE_FLAGS),
        "inputs": {
            "current_report_en_path": current_report_en_path,
            "current_report_nl_path": current_report_nl_path,
            "macro_regime_artifact_path": macro_regime_artifact_path,
        },
        "current_macro_narrative": {
            "en": current_en,
            "nl": current_nl,
        },
        "deterministic_regime_shadow_narrative_candidate": {
            "en": candidate_en,
            "nl": candidate_nl,
        },
        "comparison_markdown": _comparison_markdown(
            current_en=current_en,
            current_nl=current_nl,
            candidate_en=candidate_en,
            candidate_nl=candidate_nl,
        ),
        "blockers": blockers,
    }


def write_macro_regime_shadow_narrative(
    output_dir: Path,
    *,
    run_id: str,
    report_date: str,
    current_report_en_path: Path | None = None,
    current_report_nl_path: Path | None = None,
    macro_regime_artifact_path: Path | None = None,
    created_at_utc: str | None = None,
) -> Path:
    current_en_text = _read_text_if_available(current_report_en_path)
    current_nl_text = _read_text_if_available(current_report_nl_path)
    macro_payload = _read_json_if_available(macro_regime_artifact_path)

    artifact = build_macro_regime_shadow_narrative(
        run_id=run_id,
        report_date=report_date,
        current_report_en_text=current_en_text,
        current_report_nl_text=current_nl_text,
        macro_regime_payload=macro_payload,
        current_report_en_path=str(current_report_en_path) if current_report_en_path else None,
        current_report_nl_path=str(current_report_nl_path) if current_report_nl_path else None,
        macro_regime_artifact_path=str(macro_regime_artifact_path) if macro_regime_artifact_path else None,
        created_at_utc=created_at_utc,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"macro_regime_shadow_narrative_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--current-report-en")
    parser.add_argument("--current-report-nl")
    parser.add_argument("--macro-regime-artifact")
    args = parser.parse_args()

    path = write_macro_regime_shadow_narrative(
        Path(args.output_dir),
        run_id=args.run_id,
        report_date=args.report_date,
        current_report_en_path=Path(args.current_report_en) if args.current_report_en else None,
        current_report_nl_path=Path(args.current_report_nl) if args.current_report_nl else None,
        macro_regime_artifact_path=Path(args.macro_regime_artifact) if args.macro_regime_artifact else None,
    )
    print(
        "MACRO_REGIME_SHADOW_NARRATIVE_OK | "
        f"artifact={path} | client_facing=false | production_report=false | "
        "portfolio_action_authority=false | lane_scoring_authority=false | fundability_authority=false"
    )


if __name__ == "__main__":
    main()
