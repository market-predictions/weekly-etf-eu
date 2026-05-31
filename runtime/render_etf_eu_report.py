from __future__ import annotations

import argparse
import json
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


def _proxy_rows(proxy_map: Path) -> list[dict[str, str]]:
    # Minimal dependency-free extraction for the current YAML stub.
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


def _proxy_table_en(proxy_map: Path) -> str:
    rows = _proxy_rows(proxy_map)
    lines = ["| Theme | U.S. proxy | EU role | Status |", "|---|---|---|---|"]
    if not rows:
        lines.append("| No proxy map found | - | - | Registry required |")
        return "\n".join(lines)
    for row in rows:
        lines.append(
            f"| {row.get('theme', 'TBD')} | {row.get('us_proxy', 'TBD')} — research proxy only | {row.get('eu_role', 'TBD')} | UCITS candidate verification required |"
        )
    return "\n".join(lines)


def _proxy_table_nl(proxy_map: Path) -> str:
    rows = _proxy_rows(proxy_map)
    lines = ["| Thema | Amerikaanse proxy | EU-rol | Status |", "|---|---|---|---|"]
    if not rows:
        lines.append("| Geen proxymap gevonden | - | - | Register vereist |")
        return "\n".join(lines)
    for row in rows:
        lines.append(
            f"| {row.get('theme', 'TBD')} | {row.get('us_proxy', 'TBD')} — alleen onderzoeksproxy | {row.get('eu_role', 'TBD')} | UCITS-kandidaat moet nog worden geverifieerd |"
        )
    return "\n".join(lines)


def _cash(state: dict[str, Any]) -> float:
    return float(state.get("cash_eur") or 0.0)


def _nav(state: dict[str, Any]) -> float:
    return float(state.get("nav_eur") or state.get("cash_eur") or 0.0)


def _registry_funds(registry: Path) -> list[dict[str, Any]]:
    if not registry.exists():
        return []
    payload = _read_yaml(registry)
    return list(payload.get("funds") or [])


def _preflight_payload(pricing_preflight: Path | None, output_dir: Path) -> dict[str, Any]:
    path = pricing_preflight
    if path is None:
        path = _latest_file(output_dir / "pricing", "ucits_pricing_preflight_*.json")
    if path is None or not path.exists():
        return {}
    return _read_json(path)


def _preflight_lookup(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for row in payload.get("results") or []:
        key = (_as_str(row.get("registry_id")), _as_str(row.get("pricing_symbol_yahoo")))
        lookup[key] = row
    return lookup


def _first_line(fund: dict[str, Any]) -> dict[str, Any]:
    lines = fund.get("trading_lines") or []
    return dict(lines[0]) if lines else {}


def _pricing_status_for(fund: dict[str, Any], lookup: dict[tuple[str, str], dict[str, Any]]) -> str:
    statuses: list[str] = []
    for line in fund.get("trading_lines") or []:
        key = (_as_str(fund.get("registry_id")), _as_str(line.get("pricing_symbol_yahoo")))
        row = lookup.get(key)
        if not row:
            continue
        result = row.get("preflight_result") or {}
        status = _as_str(result.get("status")) or "not_tested"
        observed_date = _as_str(result.get("observed_date"))
        close = result.get("close")
        symbol = _as_str(line.get("pricing_symbol_yahoo"))
        if status == "priced_non_authoritative" and close is not None:
            suffix = f" {symbol}: {close:.2f}"
            if observed_date:
                suffix += f" op {observed_date}"
            statuses.append("niet-autoritatief geprijsd" + suffix)
        elif status:
            statuses.append(f"{symbol}: {status}")
    return "; ".join(statuses) if statuses else "niet getest / niet van toepassing"


def _pricing_status_for_en(fund: dict[str, Any], lookup: dict[tuple[str, str], dict[str, Any]]) -> str:
    statuses: list[str] = []
    for line in fund.get("trading_lines") or []:
        key = (_as_str(fund.get("registry_id")), _as_str(line.get("pricing_symbol_yahoo")))
        row = lookup.get(key)
        if not row:
            continue
        result = row.get("preflight_result") or {}
        status = _as_str(result.get("status")) or "not_tested"
        observed_date = _as_str(result.get("observed_date"))
        close = result.get("close")
        symbol = _as_str(line.get("pricing_symbol_yahoo"))
        if status == "priced_non_authoritative" and close is not None:
            suffix = f" {symbol}: {close:.2f}"
            if observed_date:
                suffix += f" on {observed_date}"
            statuses.append("non-authoritative price observed" + suffix)
        elif status:
            statuses.append(f"{symbol}: {status}")
    return "; ".join(statuses) if statuses else "not tested / not applicable"


def _candidate_table_nl(registry: Path, pricing_preflight: Path | None, output_dir: Path) -> str:
    funds = _registry_funds(registry)
    lookup = _preflight_lookup(_preflight_payload(pricing_preflight, output_dir))
    lines = [
        "| Rol | Instrument | ISIN | Handelslijn | Status | Amerikaanse proxy | Pricing-preflight | Portefeuille-status |",
        "|---|---|---|---|---|---|---|---|",
    ]
    if not funds:
        lines.append("| Geen kandidaten | - | - | - | register vereist | - | niet getest | geen gefinancierde positie |")
        return "\n".join(lines)
    for fund in funds:
        line = _first_line(fund)
        trading_line = f"{_as_str(line.get('exchange_ticker')) or 'TBD'} / {_as_str(line.get('trading_currency')) or 'TBD'} / {_as_str(line.get('exchange')) or 'TBD'}"
        lines.append(
            "| "
            + " | ".join([
                _as_str(fund.get("role")) or "TBD",
                _as_str(fund.get("fund_name")) or "TBD",
                _as_str(fund.get("isin")) or "TBD",
                trading_line,
                _as_str(fund.get("investability_status")) or "TBD",
                f"{_as_str(fund.get('us_research_proxy')) or 'TBD'} — alleen onderzoeksproxy",
                _pricing_status_for(fund, lookup),
                "niet gefinancierd; geen waarderingsautoriteit",
            ])
            + " |"
        )
    return "\n".join(lines)


def _candidate_table_en(registry: Path, pricing_preflight: Path | None, output_dir: Path) -> str:
    funds = _registry_funds(registry)
    lookup = _preflight_lookup(_preflight_payload(pricing_preflight, output_dir))
    lines = [
        "| Role | Instrument | ISIN | Trading line | Status | U.S. proxy | Pricing preflight | Portfolio status |",
        "|---|---|---|---|---|---|---|---|",
    ]
    if not funds:
        lines.append("| No candidates | - | - | - | registry required | - | not tested | no funded position |")
        return "\n".join(lines)
    for fund in funds:
        line = _first_line(fund)
        trading_line = f"{_as_str(line.get('exchange_ticker')) or 'TBD'} / {_as_str(line.get('trading_currency')) or 'TBD'} / {_as_str(line.get('exchange')) or 'TBD'}"
        lines.append(
            "| "
            + " | ".join([
                _as_str(fund.get("role")) or "TBD",
                _as_str(fund.get("fund_name")) or "TBD",
                _as_str(fund.get("isin")) or "TBD",
                trading_line,
                _as_str(fund.get("investability_status")) or "TBD",
                f"{_as_str(fund.get('us_research_proxy')) or 'TBD'} — research proxy only",
                _pricing_status_for_en(fund, lookup),
                "not funded; no valuation authority",
            ])
            + " |"
        )
    return "\n".join(lines)


def render_nl(state: dict[str, Any], report_date: str, proxy_map: Path, registry: Path, pricing_preflight: Path | None, output_dir: Path) -> str:
    cash = _cash(state)
    nav = _nav(state)
    return f"""# Weekly ETF EU Review | Nederlands | {report_date}

> **Status:** cash-only bootstrap. Dit is geen productiepublicatie en er is geen e-maillevering uitgevoerd.

## 1. Status

De EU/UCITS-versie van de Weekly ETF Review staat in bootstrapfase.

- **Huidige staat:** cash-only bootstrap.
- **Gefinancierde UCITS-posities:** geen.
- **Amerikaanse ETF's:** alleen onderzoeksproxy, niet investeerbaar portefeuille-instrument in dit EU-model.
- **UCITS-kandidaten:** vereisen ISIN-, KID-/PRIIPs- en handelslijnverificatie.
- **Pricing-preflight:** niet-autoritatieve connectiviteitstest, geen waarderingsautoriteit.
- **Productielevering:** uitgeschakeld.

## 2. Huidige portefeuillestaat

| Component | Waarde |
|---|---:|
| Startkapitaal | EUR 100000.00 |
| Cash | EUR {cash:.2f} |
| Belegde marktwaarde | EUR 0.00 |
| Totale portefeuillewaarde | EUR {nav:.2f} |
| Gefinancierde posities | 0 |

Er zijn nog geen UCITS ETF's gefinancierd. De portefeuille blijft volledig in cash totdat instrumenten het EU-investeerbaarheidscontract passeren.

## 3. Investeerbaarheidsfilter

Een ETF kan pas fundable worden wanneer minimaal de volgende velden zijn geverifieerd:

| Vereiste | Status |
|---|---|
| ISIN | vereist |
| UCITS-status | vereist |
| PRIIPs/KID beschikbaarheid | vereist |
| Handelsbeurs en ticker | vereist |
| Handelsvaluta | vereist |
| Pricinglijn | vereist |
| Productkosten / TER | te vullen waar beschikbaar |
| Replicatiemethode | te vullen waar beschikbaar |
| Accumulerend / distribuerend | te vullen waar beschikbaar |

## 4. Onderzoeksproxies

Amerikaanse ETF's mogen alleen als onderzoeksproxy of benchmarkreferentie worden gebruikt. Ze mogen niet als gefinancierde EU-portefeuillepositie verschijnen.

{_proxy_table_nl(proxy_map)}

## 5. UCITS-kandidatenregister

Onderstaande tabel toont registerkandidaten en een eventuele pricing-preflight. Deze tabel is **geen portefeuille**, **geen koopadvies** en **geen waarderingsautoriteit**.

{_candidate_table_nl(registry, pricing_preflight, output_dir)}

## 6. Status UCITS-register

Het UCITS-register bevat nu bootstrapkandidaten, maar er is nog geen gefinancierde modelportefeuille. Kandidaten blijven niet-gefinancierd totdat ISIN, KID/PRIIPs, handelslijn, valuta, pricingkwaliteit, liquiditeit en portefeuillerol voldoende zijn gecontroleerd.

## 7. Volgende bouwstappen

1. Verrijk het UCITS-symbolenregister met extra geverifieerde ISIN's en handelslijnen.
2. Koppel onderzoeksproxies aan daadwerkelijke UCITS-kandidaten.
3. Promoveer pricing van connectiviteitstest naar valuation-grade alleen na aparte pricing-lineagebeslissing.
4. Bouw daarna pas een gefinancierde modelportefeuille.
5. Houd productielevering uitgeschakeld totdat alle EU-validaties slagen.

## 8. Leveringsstatus

Deze output is alleen een niet-verzonden bootstraprapport. Er is geen PDF-rendering, portefeuille-executie of e-mailverzending uitgevoerd.
"""


def render_en(state: dict[str, Any], report_date: str, proxy_map: Path, registry: Path, pricing_preflight: Path | None, output_dir: Path) -> str:
    cash = _cash(state)
    nav = _nav(state)
    return f"""# Weekly ETF EU Review | English Companion | {report_date}

> **Status:** cash-only bootstrap. This is not a production publication and no email delivery was performed.

## 1. Status

The EU/UCITS version of the Weekly ETF Review is in bootstrap mode.

- **Current state:** cash-only bootstrap.
- **Funded UCITS holdings:** none.
- **U.S. ETFs:** research proxies only, not investable portfolio instruments in this EU model.
- **UCITS candidates:** require ISIN, KID/PRIIPs and trading-line verification.
- **Pricing preflight:** non-authoritative connectivity test, no valuation authority.
- **Production delivery:** disabled.

## 2. Current portfolio state

| Component | Value |
|---|---:|
| Starting capital | EUR 100000.00 |
| Cash | EUR {cash:.2f} |
| Invested market value | EUR 0.00 |
| Total portfolio value | EUR {nav:.2f} |
| Funded positions | 0 |

No UCITS ETFs are funded yet. The portfolio remains fully in cash until instruments pass the EU investability contract.

## 3. Investability gate

An ETF can become fundable only after at least the following fields are verified:

| Requirement | Status |
|---|---|
| ISIN | required |
| UCITS status | required |
| PRIIPs/KID availability | required |
| Exchange and ticker | required |
| Trading currency | required |
| Pricing line | required |
| Product cost / TER | to be added where available |
| Replication method | to be added where available |
| Accumulating / distributing | to be added where available |

## 4. Research proxies

U.S. ETFs may be used only as research proxies or benchmark references. They must not appear as funded EU portfolio holdings.

{_proxy_table_en(proxy_map)}

## 5. UCITS candidate registry

The table below shows registry candidates and optional pricing preflight status. This table is **not a portfolio**, **not a buy recommendation** and **not valuation authority**.

{_candidate_table_en(registry, pricing_preflight, output_dir)}

## 6. UCITS registry status

The UCITS registry now contains bootstrap candidates, but there is no funded model portfolio yet. Candidates remain unfunded until ISIN, KID/PRIIPs, trading line, currency, pricing quality, liquidity and portfolio role are sufficiently checked.

## 7. Next build steps

1. Enrich the UCITS symbol registry with additional verified ISINs and trading lines.
2. Map research proxies to actual UCITS candidates.
3. Promote pricing from connectivity test to valuation-grade only after a separate pricing-lineage decision.
4. Only then build a funded model portfolio.
5. Keep production delivery disabled until all EU validations pass.

## 8. Delivery status

This output is a non-delivered bootstrap report only. No PDF rendering, portfolio execution or email delivery was performed.
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
    print(f"ETF_EU_REPORT_RENDER_OK | en={en_path} | nl={nl_path} | candidate_registry=True | delivery=false")


if __name__ == "__main__":
    main()
