"""Diagnostic: Yahoo vs Alpha Vantage closes for two lines, last 8 days."""
from datetime import date, timedelta
from v2 import sources as S
end = date.today(); start = end - timedelta(days=12)
for t in ("DFEN", "L0CK", "SXR8"):
    y = S.yahoo(t, "Xetra", start, end)
    a = S.alpha_vantage(t, "Xetra")
    S.pause(13)
    for d in sorted(set(y.closes) | {k for k in a.closes if k >= start.isoformat()}):
        print(f"DIAG {t} {d} yahoo={y.closes.get(d)} av={a.closes.get(d)}", flush=True)
    print(f"DIAG {t} yahoo_sym={y.symbol} av_sym={a.symbol} yahoo_err={y.error} av_err={a.error}", flush=True)
