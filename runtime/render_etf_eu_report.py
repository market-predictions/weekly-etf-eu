from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

DEFAULT_STATE = Path("output/etf_eu_portfolio_state.json")
DEFAULT_PROXY_MAP = Path("config/ucits_benchmark_proxy_map.yml")
DEFAULT_REGISTRY = Path("config/ucits_symbol_registry.yml")
DEFAULT_PRICING_DIR = Path("output/pricing")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to render UCITS candidate tables")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _suffix(report_date: str) -> str:
    y, m, d = report_date.split("-")
    return f"{y[2:]}{m}{d}"


def _latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern))
    return files[-1] if files else None


def _as_str(value: Any) -> str:
    return str(value if value is not None else "").strip()


def _usable_close(value: object) -> float | None:
    try:
        close = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if not math.isfinite(close) or close <= 0:
        return None
    return close


def _cash(state: dict[str, Any]) -> float:
    return float(state.get("cash_eur") or 0.0)


def _nav(state: dict[str, Any]) -> float:
    return float(state.get("nav_eur") or state.get("cash_eur") or 0.0)


def _proxy_rows(proxy_map: Path) -> list[dict[str, str]]:
    if not proxy_map.exists():
        return []
    rows: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw in proxy_map.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("- theme:"):
            if current:
                rows.append(current)
            current = {"theme": line.split(":", 1)[1].strip()}
        elif current and line.startswith("us_proxy:"):
            current["us_proxy"] = line.split(":", 1)[1].strip()
        elif current and line.startswith("benchmark:"):
            current["benchmark"] = line.split(":", 1)[1].strip()
        elif current and line.startswith("eu_role:"):
            current["eu_role"] = line.split(":", 1)[1].strip()
    if current:
        rows.append(current)
    return rows


def _proxy_appendix_nl(proxy_map: Path) -> str:
    rows = _proxy_rows(proxy_map)
    lines = ["| Thema | Onderzoeksreferentie | EU-rol | Status |", "|---|---|---|---|"]
    if not rows:
        lines.append("| Geen proxymap gevonden | - | - | Register vereist |")
        return "\n".join(lines)
    for row in rows:
        lines.append(
            f"| {row.get('theme', 'n.v.t.')} | {row.get('us_proxy', 'n.v.t.')} | {row.get('eu_role', 'n.v.t.')} | Alleen onderzoeksreferentie; niet investeerbaar in het EU-model |"
        )
    return "\n".join(lines)


def _proxy_appendix_en(proxy_map: Path) -> str:
    rows = _proxy_rows(proxy_map)
    lines = ["| Theme | Research reference | EU role | Status |", "|---|---|---|---|"]
    if not rows:
        lines.append("| No proxy map found | - | - | Registry required |")
        return "\n".join(lines)
    for row in rows:
        lines.append(
            f"| {row.get('theme', 'n/a')} | {row.get('us_proxy', 'n/a')} | {row.get('eu_role', 'n/a')} | Research reference only; not investable in the EU model |"
        )
    return "\n".join(lines)


def _registry_funds(registry: Path) -> list[dict[str, Any]]:
    if not registry.exists():
        return []
    payload = _read_yaml(registry)
    return list(payload.get("funds") or [])


def _preflight_payload(pricing_preflight: Path | None, output_dir: Path) -> dict[str, Any]:
    path = pricing_preflight or _latest_file(output_dir / "pricing", "ucits_pricing_preflight_*.json")
    if path is None or not path.exists():
        return {}
    return _read_json(path)


def _preflight_lookup(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for row in payload.get("results") or []:
        key = (_as_str(row.get("registry_id")), _as_str(row.get("pricing_symbol_yahoo")))
        lookup[key] = row
    return lookup


def _verified_lines(registry: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fund in _registry_funds(registry):
        isin = _as_str(fund.get("isin"))
        if not isin or isin == "TBD":
            continue
        if _as_str(fund.get("instrument_type")) != "ETF":
            continue
        if "confirmed" not in _as_str(fund.get("ucits_status")):
            continue
        for line in fund.get("trading_lines") or []:
            symbol = _as_str(line.get("pricing_symbol_yahoo"))
            exchange = _as_str(line.get("exchange"))
            ticker = _as_str(line.get("exchange_ticker"))
            currency = _as_str(line.get("trading_currency"))
            if not symbol or "pending" in symbol.lower() or not exchange or "pending" in exchange.lower():
                continue
            rows.append({
                "registry_id": _as_str(fund.get("registry_id")),
                "role": _as_str(fund.get("role")),
                "fund_name": _as_str(fund.get("fund_name")),
                "isin": isin,
                "ticker": ticker,
                "currency": currency,
                "exchange": exchange,
                "pricing_symbol_yahoo": symbol,
                "status": _as_str(fund.get("investability_status")) or "verified_candidate_not_funded",
            })
    return rows


def _pricing_status(registry_id: str, symbol: str, lookup: dict[tuple[str, str], dict[str, Any]], *, language: str) -> str:
    no_close = "geen bruikbare close; diagnostiek vereist" if language == "nl" else "no usable close; diagnostics required"
    row = lookup.get((registry_id, symbol))
    if not row:
        return "diagnostiek vereist" if language == "nl" else "diagnostics required"
    result = row.get("preflight_result") or {}
    status = _as_str(result.get("status")) or "not_tested"
    usable_close = _usable_close(result.get("close"))
    observed_date = _as_str(result.get("observed_date"))
    if status == "priced_non_authoritative":
        if usable_close is None:
            return no_close
        label = "niet-autoritatieve close" if language == "nl" else "non-authoritative close"
        suffix = f"{label}: {usable_close:.2f}"
        if observed_date:
            suffix += f" ({observed_date})"
        return suffix
    return status


def _watchlist_table(registry: Path, pricing_preflight: Path | None, output_dir: Path, *, language: str) -> str:
    rows = _verified_lines(registry)
    lookup = _preflight_lookup(_preflight_payload(pricing_preflight, output_dir))
    if language == "nl":
        lines = ["| Rol | UCITS ETF | ISIN | Handelslijn | Datastatus | Portefeuille-status |", "|---|---|---|---|---|---|"]
        if not rows:
            lines.append("| Geen geverifieerde handelslijnen | - | - | - | Diagnostiek vereist | Geen gefinancierde positie |")
        for row in rows:
            trading_line = f"{row['ticker']} / {row['currency']} / {row['exchange']}"
            lines.append("| " + " | ".join([
                row["role"],
                row["fund_name"],
                row["isin"],
                trading_line,
                _pricing_status(row["registry_id"], row["pricing_symbol_yahoo"], lookup, language="nl"),
                "Niet gefinancierd; geen waarderings- of fundingautoriteit",
            ]) + " |")
        return "\n".join(lines)
    lines = ["| Role | UCITS ETF | ISIN | Trading line | Data status | Portfolio status |", "|---|---|---|---|---|---|"]
    if not rows:
        lines.append("| No verified trading lines | - | - | - | Diagnostics required | No funded position |")
    for row in rows:
        trading_line = f"{row['ticker']} / {row['currency']} / {row['exchange']}"
        lines.append("| " + " | ".join([
            row["role"],
            row["fund_name"],
            row["isin"],
            trading_line,
            _pricing_status(row["registry_id"], row["pricing_symbol_yahoo"], lookup, language="en"),
            "Not funded; no valuation or funding authority",
        ]) + " |")
    return "\n".join(lines)


def render_nl(state: dict[str, Any], report_date: str, proxy_map: Path, registry: Path, pricing_preflight: Path | None, output_dir: Path) -> str:
    cash = _cash(state)
    nav = _nav(state)
    return f"""# Weekly ETF EU Review | Nederlands | {report_date}

> **Pakketstatus:** EU/UCITS-clientpakket in validatiefase. Dit rapport is geen koopadvies, geen portefeuille-opdracht en geen waarderingsautoriteit.

## 1. Kernsamenvatting

De EU/UCITS-versie gebruikt uitsluitend UCITS-handelslijnen als potentieel investeerbare instrumenten. Amerikaanse ETF-symbolen horen niet in de primaire clienttabel en worden alleen in de bijlage als onderzoeksreferentie bewaard.

- **Modelstaat:** cash-only, geen gefinancierde UCITS-posities.
- **Beslissing:** nog geen allocatie; eerst datakwaliteit en handelslijnverificatie afronden.
- **Koersinformatie:** alleen niet-autoritatieve connectiviteits- of diagnostische observatie totdat aparte waarderingslineage is goedgekeurd.

## 2. Portefeuille-overzicht

| Component | Waarde |
|---|---:|
| Startkapitaal | EUR 100000.00 |
| Cash | EUR {cash:.2f} |
| Belegde marktwaarde | EUR 0.00 |
| Totale portefeuillewaarde | EUR {nav:.2f} |
| Gefinancierde posities | 0 |

## 3. UCITS observatielijst

Deze tabel toont alleen ISIN-first UCITS-handelslijnen die voldoende zijn om in de primaire clientwatchlist te staan. Onopgeloste of beleidsmatige items staan niet in deze hoofdtabel.

{_watchlist_table(registry, pricing_preflight, output_dir, language="nl")}

## 4. Koersvalidatie en datakwaliteit

Koersen in dit pakket zijn diagnostisch. Een positieve close in de pipeline bewijst connectiviteit, maar creëert geen waarderingsautoriteit en geen fundingbesluit.

## 5. Besliscockpit / Volgende actie

| Vraag | Antwoord |
|---|---|
| Is er een gefinancierde positie? | Nee |
| Is er koopadvies? | Nee |
| Is pricing valuation-grade? | Nee |
| Volgende stap | PDF-pakket en UCITS close-fetch validatie afronden vóór gecontroleerde herverzending |

## 6. Bijlage: onderzoeksproxies en diagnostiek

Onderzoeksreferenties hieronder zijn niet investeerbaar in dit EU-model. Ze mogen niet worden gelezen als portefeuille-instrument.

{_proxy_appendix_nl(proxy_map)}
"""


def render_en(state: dict[str, Any], report_date: str, proxy_map: Path, registry: Path, pricing_preflight: Path | None, output_dir: Path) -> str:
    cash = _cash(state)
    nav = _nav(state)
    return f"""# Weekly ETF EU Review | English Companion | {report_date}

> **Package status:** EU/UCITS client package under validation. This report is not advice, not a portfolio instruction and not valuation authority.

## 1. Executive summary

The EU/UCITS version uses UCITS trading lines only as potentially investable instruments. U.S. ETF symbols do not belong in the primary client table and are retained only in the appendix as research references.

- **Model state:** cash-only, no funded UCITS positions.
- **Decision:** no allocation yet; complete data quality and trading-line verification first.
- **Price information:** non-authoritative connectivity or diagnostics only until separate valuation lineage is approved.

## 2. Portfolio overview

| Component | Value |
|---|---:|
| Starting capital | EUR 100000.00 |
| Cash | EUR {cash:.2f} |
| Invested market value | EUR 0.00 |
| Total portfolio value | EUR {nav:.2f} |
| Funded positions | 0 |

## 3. UCITS watchlist

This table shows only ISIN-first UCITS trading lines that are clean enough for the primary client watchlist. Unresolved or policy-review items are excluded from this main table.

{_watchlist_table(registry, pricing_preflight, output_dir, language="en")}

## 4. Price validation and data quality

Prices in this package are diagnostic. A positive close in the pipeline proves connectivity, but it does not create valuation authority or a funding decision.

## 5. Decision cockpit / next action

| Question | Answer |
|---|---|
| Is there a funded position? | No |
| Is this advice? | No |
| Is pricing valuation-grade? | No |
| Next step | Complete PDF package and UCITS close-fetch validation before controlled resend |

## 6. Appendix: research proxies and diagnostics

The research references below are not investable instruments in this EU model. They must not be read as portfolio instruments.

{_proxy_appendix_en(proxy_map)}
"""


def write_reports(output_dir: Path, state_path: Path, proxy_map: Path, registry: Path, pricing_preflight: Path | None, report_date: str) -> tuple[Path, Path]:
    state = _read_json(state_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = _suffix(report_date)
    en_path = output_dir / f"weekly_etf_eu_review_{suffix}.md"
    nl_path = output_dir / f"weekly_etf_eu_review_nl_{suffix}.md"
    en_path.write_text(render_en(state, report_date, proxy_map, registry, pricing_preflight, output_dir), encoding="utf-8")
    nl_path.write_text(render_nl(state, report_date, proxy_map, registry, pricing_preflight, output_dir), encoding="utf-8")
    return en_path, nl_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    parser.add_argument("--proxy-map", default=str(DEFAULT_PROXY_MAP))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--pricing-preflight", default=None)
    parser.add_argument("--report-date", default=date.today().isoformat())
    args = parser.parse_args()
    en_path, nl_path = write_reports(
        Path(args.output_dir),
        Path(args.state),
        Path(args.proxy_map),
        Path(args.registry),
        Path(args.pricing_preflight) if args.pricing_preflight else None,
        args.report_date,
    )
    print(f"ETF_EU_REPORT_RENDER_OK | en={en_path} | nl={nl_path} | client_surface=cleaned | delivery_package_pending=true")


if __name__ == "__main__":
    main()
