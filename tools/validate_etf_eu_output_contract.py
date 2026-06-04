from __future__ import annotations

import argparse
import re
from pathlib import Path

EU_REPORT_RE = re.compile(r"^weekly_etf_eu_review(?:_nl)?_\d{6}\.md$")
US_PROXY_TICKERS = ["SPY", "QQQ", "SMH", "GLD", "GSG", "PPA", "PAVE", "URNM", "IWM", "TLT", "KWEB", "ICLN", "SOXX", "ITA", "GRID", "URA", "NLR"]
REQUIRED_EN_PHRASES = [
    "cash-only bootstrap",
    "Funded UCITS holdings: none",
    "research proxies only",
    "require ISIN, KID/PRIIPs and trading-line verification",
    "Production delivery: disabled",
    "No PDF rendering, portfolio execution or email delivery was performed",
]
REQUIRED_NL_PHRASES = [
    "cash-only bootstrap",
    "Gefinancierde UCITS-posities: geen",
    "alleen onderzoeksproxy",
    "vereisen ISIN-, KID-/PRIIPs- en handelslijnverificatie",
    "Productielevering: uitgeschakeld",
    "geen PDF-rendering, portefeuille-executie of e-mailverzending uitgevoerd",
]
STRICT_PRODUCTION_NL_PHRASES = [
    "Productierapport-volwassenheid",
    "Nederlandse hoofdrapportage",
    "primaire clientrapportage",
    "geen gefinancierde UCITS-posities",
    "geen koopadvies",
    "geen portefeuille-mutatie",
    "geen productielevering",
    "geen delivery receipt",
]
STRICT_PRODUCTION_EN_PHRASES = [
    "Production report maturity",
    "Dutch report is the primary client report",
    "companion/operator-facing version",
    "no funded UCITS holdings",
    "no buy recommendation",
    "no portfolio mutation",
    "no production delivery",
    "no delivery receipt",
]
ALLOWED_PROXY_CONTEXT = [
    "research proxy",
    "research proxies",
    "onderzoeksproxy",
    "onderzoeksproxies",
    "benchmark",
    "proxy",
    "not investable",
    "niet investeerbaar",
    "not an investable eu holding",
    "niet als gefinancierde eu-portefeuillepositie",
]
FORBIDDEN_HOLDING_CONTEXT = [
    "funded holding",
    "funded holdings",
    "current holding",
    "current holdings",
    "portfolio holding",
    "portfolio holdings",
    "gefundeerde positie",
    "gefinancierde positie",
    "huidige positie",
    "portefeuillepositie",
]
FORBIDDEN_PRODUCTION_CLAIMS = [
    "funding_authority=true",
    "portfolio_mutation=true",
    "production_delivery=true",
    "delivery completed",
    "delivery receipt exists",
    "pdf generated",
    "email sent",
    "waarderingsautoriteit: ja",
    "valuation authority: yes",
    "koopadvies: ja",
]


def _normalized_markdown(text: str) -> str:
    """Normalize cosmetic markdown so contract checks test semantics, not bold markers."""
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def _lines_with_ticker(text: str, ticker: str) -> list[str]:
    pattern = re.compile(rf"\b{re.escape(ticker)}\b")
    return [line.strip() for line in text.splitlines() if pattern.search(line)]


def _is_allowed_proxy_line(line: str) -> bool:
    lower = line.lower()
    return any(token in lower for token in ALLOWED_PROXY_CONTEXT)


def _has_forbidden_holding_context(line: str) -> bool:
    lower = line.lower()
    return any(token in lower for token in FORBIDDEN_HOLDING_CONTEXT) and not _is_allowed_proxy_line(line)


def _validate_strict_production_maturity(path: Path, normalized_text: str, *, is_nl: bool) -> None:
    required = STRICT_PRODUCTION_NL_PHRASES if is_nl else STRICT_PRODUCTION_EN_PHRASES
    missing = [phrase for phrase in required if phrase not in normalized_text]
    if missing:
        raise RuntimeError(
            f"EU production Dutch-first contract failed for {path.name}: missing required production maturity phrase(s): {', '.join(missing)}"
        )
    lowered = normalized_text.lower()
    for phrase in FORBIDDEN_PRODUCTION_CLAIMS:
        if phrase.lower() in lowered:
            raise RuntimeError(f"EU production Dutch-first contract failed for {path.name}: forbidden production claim present: {phrase}")


def _validate_report(path: Path, *, require_production_dutch_first: bool = False) -> None:
    if not EU_REPORT_RE.match(path.name):
        raise RuntimeError(f"EU output contract failed: unexpected EU report filename: {path.name}")
    text = path.read_text(encoding="utf-8")
    normalized_text = _normalized_markdown(text)
    is_nl = "_nl_" in path.name
    required = REQUIRED_NL_PHRASES if is_nl else REQUIRED_EN_PHRASES
    missing = [phrase for phrase in required if phrase not in normalized_text]
    if missing:
        raise RuntimeError(f"EU output contract failed for {path.name}: missing required phrase(s): {', '.join(missing)}")
    if "weekly_analysis_pro" in normalized_text:
        raise RuntimeError(f"EU output contract failed for {path.name}: inherited U.S. report filename leaked into EU report body")
    for ticker in US_PROXY_TICKERS:
        for line in _lines_with_ticker(text, ticker):
            normalized_line = _normalized_markdown(line)
            if _has_forbidden_holding_context(normalized_line):
                raise RuntimeError(f"EU output contract failed for {path.name}: U.S. proxy {ticker} appears in holding context: {normalized_line[:220]}")
            if ticker in normalized_line and not _is_allowed_proxy_line(normalized_line):
                # Permit explicit mapping rows only if the row labels the ticker as proxy/reference.
                if normalized_line.startswith("|"):
                    raise RuntimeError(f"EU output contract failed for {path.name}: U.S. proxy {ticker} appears in table without proxy context: {normalized_line[:220]}")
    if require_production_dutch_first or "Productierapport-volwassenheid" in normalized_text or "Production report maturity" in normalized_text:
        _validate_strict_production_maturity(path, normalized_text, is_nl=is_nl)
    print(f"ETF_EU_OUTPUT_CONTRACT_OK | report={path.name} | language={'nl' if is_nl else 'en'}")


def validate(output_dir: Path, *, require_production_dutch_first: bool = False) -> None:
    reports = sorted(path for path in output_dir.glob("weekly_etf_eu_review*.md") if path.is_file())
    if not reports:
        raise RuntimeError("EU output contract failed: no weekly_etf_eu_review*.md reports found")
    us_named = [path.name for path in output_dir.glob("weekly_analysis_pro_*.md") if path.is_file()]
    if us_named:
        print("ETF_EU_OUTPUT_WARNING | inherited_us_named_reports_present_as_clone_artifacts=" + ",".join(us_named[:5]))
    has_en = any("_nl_" not in path.name for path in reports)
    has_nl = any("_nl_" in path.name for path in reports)
    if not has_en or not has_nl:
        raise RuntimeError("EU output contract failed: expected both English companion and Dutch primary markdown outputs")
    for report in reports:
        _validate_report(report, require_production_dutch_first=require_production_dutch_first)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--require-production-dutch-first", action="store_true")
    args = parser.parse_args()
    validate(Path(args.output_dir), require_production_dutch_first=args.require_production_dutch_first)


if __name__ == "__main__":
    main()
