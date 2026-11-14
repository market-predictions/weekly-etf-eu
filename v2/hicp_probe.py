"""Find a euro-area HICP inflation series that is current (one-off probe)."""
from __future__ import annotations

from datetime import date

from v2 import macro as M

CANDIDATES = [
    ("ecb", "ICP/M.U2.N.000000.4.ANR"),
    ("ecb", "ICP/M.U2.N.TOTAL.4.ANR"),
    ("ecb", "ICP/M.U2.Y.000000.3.ANR"),
    ("eurostat", "prc_hicp_manr:EA:CP00"),
    ("eurostat", "prc_hicp_manr:EA:TOTAL"),
    ("eurostat", "prc_hicp_minr:EA:CP00"),
    ("eurostat", "prc_hicp_minr:EA:TOTAL"),
    ("eurostat", "prc_hicp_manr:EA21:CP00"),
    ("eurostat", "prc_hicp_manr:EA20:CP00"),
]


def main() -> None:
    start = date(2025, 6, 1)
    for src, key in CANDIDATES:
        try:
            obs = M.FETCHERS[src](key, start)
            print(f"HICP {src} {key}: n={len(obs)} last={obs[-1] if obs else None}")
        except Exception as exc:
            print(f"HICP {src} {key}: error {type(exc).__name__}: {str(exc)[:100]}")


if __name__ == "__main__":
    main()
