"""Live macro context from official sources (no hard-coded stances).

Each indicator: latest value, its date, the value ~1 month earlier, and a
staleness flag. Missing or stale data is reported as such — never filled in.

Sources: ECB Data Portal (no key) and FRED CSV (no key).
"""
from __future__ import annotations

import csv
import io
import json
from datetime import date, timedelta
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
UA = {"User-Agent": "Mozilla/5.0 (weekly-etf-eu v2)"}

# id: (source, series key, label EN, label NL, unit, max_age_days)
SERIES = {
    "ecb_deposit_rate": ("ecb", "FM/D.U2.EUR.4F.KR.DFR.LEV", "ECB deposit rate", "ECB-depositorente", "%", 10),
    "fed_funds_upper": ("fred", "DFEDTARU", "Fed funds target (upper)", "Fed funds-doel (bovengrens)", "%", 10),
    "euro_10y_yield": ("ecb", "YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y", "Euro area 10y government yield (AAA)", "Rente 10-jaars staatsobligaties eurozone (AAA)", "%", 10),
    "eurusd": ("ecb", "EXR/D.USD.EUR.SP00.A", "EUR/USD", "EUR/USD", "", 10),
    "euro_inflation": ("ecb", "ICP/M.U2.N.000000.4.ANR", "Euro area inflation (HICP, y/y)", "Inflatie eurozone (HICP, j/j)", "%", 75),
}


def _ecb(key: str, start: date) -> list[tuple[str, float]]:
    flow, series = key.split("/", 1)
    r = requests.get(f"https://data-api.ecb.europa.eu/service/data/{flow}/{series}",
                     params={"startPeriod": start.isoformat(), "format": "csvdata"}, headers=UA, timeout=30)
    r.raise_for_status()
    out = []
    for row in csv.DictReader(io.StringIO(r.text)):
        if row.get("OBS_VALUE") not in (None, ""):
            p = row["TIME_PERIOD"]
            p = p + "-01" if len(p) == 7 else p  # monthly → first of month
            out.append((p, float(row["OBS_VALUE"])))
    return sorted(out)


def _fred(key: str, start: date) -> list[tuple[str, float]]:
    r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv", params={"id": key, "cosd": start.isoformat()}, headers=UA, timeout=30)
    r.raise_for_status()
    out = []
    for row in csv.reader(io.StringIO(r.text)):
        if len(row) == 2 and row[1] not in ("", ".") and row[0][:1].isdigit():
            out.append((row[0], float(row[1])))
    return sorted(out)


def fetch(asof: date) -> dict:
    start = asof - timedelta(days=500)
    result = {}
    for sid, (src, key, en, nl, unit, max_age) in SERIES.items():
        item = {"label_en": en, "label_nl": nl, "unit": unit, "source": src, "series": key}
        try:
            obs = [(d, v) for d, v in (_ecb(key, start) if src == "ecb" else _fred(key, start)) if d <= asof.isoformat()]
            if not obs:
                raise ValueError("no observations")
            d, v = obs[-1]
            month_ago = (date.fromisoformat(d) - timedelta(days=30)).isoformat()
            prev = [x for x in obs if x[0] <= month_ago]
            year_ago = (date.fromisoformat(d) - timedelta(days=365)).isoformat()
            prev_y = [x for x in obs if x[0] <= year_ago]
            item.update({
                "date": d, "value": round(v, 4),
                "value_1m_ago": round(prev[-1][1], 4) if prev else None,
                "value_1y_ago": round(prev_y[-1][1], 4) if prev_y else None,
                "stale": (asof - date.fromisoformat(d)).days > max_age,
                "available": True,
            })
        except Exception as exc:
            item.update({"available": False, "error": f"{type(exc).__name__}: {str(exc)[:80]}"})
        result[sid] = item
    return result


def main() -> None:
    m = fetch(date.today())
    for k, v in m.items():
        print(f"MACRO {k}: {json.dumps(v)}")


if __name__ == "__main__":
    main()
