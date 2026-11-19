"""Diagnostic: raw Yahoo chart tail + meta for Xetra lines."""
from datetime import date, datetime, timedelta, timezone
from v2 import sources as S
end = date.today(); start = end - timedelta(days=6)
p1 = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp())
p2 = int(datetime(end.year, end.month, end.day, 23, 59, tzinfo=timezone.utc).timestamp())
for sym in ("DFEN.DE", "L0CK.DE", "SXR8.DE", "VWCE.DE", "EUNA.DE"):
    r = S._get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}", period1=p1, period2=p2, interval="1d")
    c = r.json()["chart"]["result"][0]
    m = c["meta"]
    ts = c.get("timestamp") or []
    cl = c["indicators"]["quote"][0].get("close") or []
    print(f"DIAG {sym} rmt={datetime.fromtimestamp(m.get('regularMarketTime', 0), tz=timezone.utc)} rmp={m.get('regularMarketPrice')} "
          f"prev={m.get('chartPreviousClose')} period={m.get('currentTradingPeriod', {}).get('regular')}", flush=True)
    for t, v in zip(ts, cl):
        print(f"DIAG   {sym} {datetime.fromtimestamp(t, tz=timezone.utc)} close={v}", flush=True)
