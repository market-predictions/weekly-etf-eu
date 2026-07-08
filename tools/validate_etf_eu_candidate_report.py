from __future__ import annotations

import argparse
import re
from pathlib import Path

EU_REPORT_RE = re.compile(r"^weekly_etf_eu_review(?:_nl)?_(\d{6})\.md$")

REQUIRED_NL = [
    "UCITS-kandidatenregister",
    "geen portefeuille",
    "geen koopadvies",
    "geen waarderingsautoriteit",
    "niet gefinancierd; geen waarderingsautoriteit",
    "Pricing-preflight: niet-autoritatieve connectiviteitstest",
]
REQUIRED_EN = [
    "UCITS candidate registry",
    "not a portfolio",
    "not a buy recommendation",
    "not valuation authority",
    "not funded; no valuation authority",
    "Pricing preflight: non-authoritative connectivity test",
]
FORBIDDEN = [
    "funded UCITS position: CSPX",
    "funded UCITS holding: CSPX",
    "gefinancierde UCITS-positie: CSPX",
    "waarderingsautoriteit: ja",
    "valuation authority: yes",
]


def _normalize(text: str) -> str:
    text = text.replace("**", "")
    text = text.replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def _is_canonical_eu_report(path: Path) -> bool:
    return EU_REPORT_RE.match(path.name) is not None


def _report_suffix(path: Path) -> str:
    match = EU_REPORT_RE.match(path.name)
    if not match:
        raise RuntimeError(f"EU candidate report validation failed: unexpected EU report filename: {path.name}")
    return match.group(1)


def _discover_canonical_reports(output_dir: Path) -> list[Path]:
    discovered = sorted(path for path in output_dir.glob("weekly_etf_eu_review*.md") if path.is_file())
    canonical = [path for path in discovered if _is_canonical_eu_report(path)]
    ignored = [path.name for path in discovered if not _is_canonical_eu_report(path)]
    if ignored:
        print("ETF_EU_CANDIDATE_REPORT_WARNING | ignored_non_canonical_eu_report_artifacts=" + ",".join(ignored[:10]))
    return canonical


def _select_reports_for_suffix(reports: list[Path], report_suffix: str) -> list[Path]:
    selected = [path for path in reports if _report_suffix(path) == report_suffix]
    if not selected:
        available = sorted({_report_suffix(path) for path in reports})
        raise RuntimeError(
            "EU candidate report validation failed: "
            f"no canonical reports found for requested report_suffix={report_suffix}; "
            f"available_canonical_suffixes={','.join(available) if available else 'none'}"
        )
    return selected


def _select_latest_report_pair(reports: list[Path]) -> list[Path]:
    latest_suffix = max(_report_suffix(path) for path in reports)
    return _select_reports_for_suffix(reports, latest_suffix)


def _validate_one(path: Path) -> None:
    if not _is_canonical_eu_report(path):
        raise RuntimeError(f"EU candidate report validation failed: unexpected EU report filename: {path.name}")
    text = path.read_text(encoding="utf-8")
    normalized = _normalize(text)
    is_nl = "_nl_" in path.name
    required = REQUIRED_NL if is_nl else REQUIRED_EN
    missing = [phrase for phrase in required if phrase not in normalized]
    if missing:
        raise RuntimeError(f"EU candidate report validation failed for {path.name}: missing {', '.join(missing)}")
    for phrase in FORBIDDEN:
        if phrase.lower() in normalized.lower():
            raise RuntimeError(f"EU candidate report validation failed for {path.name}: forbidden phrase present: {phrase}")
    if "CSPX" in normalized and "not funded" not in normalized and "niet gefinancierd" not in normalized:
        raise RuntimeError(f"EU candidate report validation failed for {path.name}: CSPX appears without explicit non-funded context")
    if "priced_non_authoritative" in normalized and "no valuation authority" not in normalized and "geen waarderingsautoriteit" not in normalized:
        raise RuntimeError(f"EU candidate report validation failed for {path.name}: pricing status appears without no-valuation-authority context")
    print(f"ETF_EU_CANDIDATE_REPORT_OK | report={path.name} | language={'nl' if is_nl else 'en'}")


def validate(output_dir: Path, *, report_suffix: str | None = None) -> None:
    reports = _discover_canonical_reports(output_dir)
    if not reports:
        raise RuntimeError("EU candidate report validation failed: no canonical weekly_etf_eu_review*.md reports found")
    reports_to_validate = _select_reports_for_suffix(reports, report_suffix) if report_suffix else _select_latest_report_pair(reports)
    has_en = any("_nl_" not in p.name for p in reports_to_validate)
    has_nl = any("_nl_" in p.name for p in reports_to_validate)
    if not has_en or not has_nl:
        raise RuntimeError("EU candidate report validation failed: expected Dutch and English report pair")
    for path in reports_to_validate:
        _validate_one(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--report-suffix", default=None, help="Validate only the canonical report pair for YYMMDD suffix, e.g. 260708")
    args = parser.parse_args()
    validate(Path(args.output_dir), report_suffix=args.report_suffix)


if __name__ == "__main__":
    main()
