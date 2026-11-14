"""Scan + decision engine for Weekly ETF EU v2. Pure functions, no network.

scan()   ranks the universe on momentum and trend at a given date.
decide() turns the scan + current holdings into target weights and trades,
         applying every rule in policy.yml. Each trade carries a structured
         reason so the report can explain it without inventing anything.
"""
from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field

TAG_KEYS = ("theme", "segment", "region", "factor")


# ── Price access ─────────────────────────────────────────────────────────────
class Prices:
    """Daily closes per instrument with as-of lookups (no look-ahead)."""

    def __init__(self, rows: list[dict]):
        self.dates: dict[str, list[str]] = {}
        self.closes: dict[str, list[float]] = {}
        for r in sorted(rows, key=lambda x: (x["id"], x["date"])):
            self.dates.setdefault(r["id"], []).append(r["date"])
            self.closes.setdefault(r["id"], []).append(float(r["close"]))

    def upto(self, iid: str, d: str) -> list[float]:
        ds = self.dates.get(iid, [])
        return self.closes.get(iid, [])[: bisect.bisect_right(ds, d)]

    def close(self, iid: str, d: str, max_stale_days: int = 5) -> float | None:
        ds = self.dates.get(iid, [])
        i = bisect.bisect_right(ds, d) - 1
        if i < 0:
            return None
        from datetime import date as _d
        gap = (_d.fromisoformat(d) - _d.fromisoformat(ds[i])).days
        return self.closes[iid][i] if gap <= max_stale_days else None


# ── Scan ─────────────────────────────────────────────────────────────────────
def _ret(series: list[float], days: int) -> float | None:
    if len(series) <= days:
        return None
    return series[-1] / series[-1 - days] - 1


def _vol(series: list[float], days: int) -> float | None:
    if len(series) <= days:
        return None
    rets = [series[i] / series[i - 1] - 1 for i in range(len(series) - days, len(series))]
    m = sum(rets) / len(rets)
    return math.sqrt(sum((r - m) ** 2 for r in rets) / (len(rets) - 1)) * math.sqrt(252)


def tags(inst: dict) -> set[tuple[str, str]]:
    return {(k, inst[k]) for k in TAG_KEYS if inst.get(k)}


def scan(prices: Prices, universe: list[dict], policy: dict, d: str) -> dict:
    sc = policy["scoring"]
    wins = sc["momentum_windows_days"]
    min_hist = policy["satellites"]["min_history_days"]
    rows = []
    for inst in universe:
        s = prices.upto(inst["id"], d)
        if not s or prices.close(inst["id"], d) is None:
            continue
        sma = sum(s[-sc["trend_sma_days"]:]) / sc["trend_sma_days"] if len(s) >= sc["trend_sma_days"] else None
        row = {
            "id": inst["id"], "name": inst["name"], "sleeve": inst["sleeve"], "asset_class": inst["asset_class"],
            "tags": sorted(f"{k}:{v}" for k, v in tags(inst)),
            "close": s[-1], "sma200": round(sma, 4) if sma else None,
            "trend_up": (s[-1] > sma) if sma else None,
            "vol": round(_vol(s, sc["volatility_days"]) or 0, 4) if len(s) > sc["volatility_days"] else None,
        }
        for w in wins:
            r = _ret(s, w)
            row[f"r{w}"] = round(r, 6) if r is not None else None
        row["rankable"] = inst["sleeve"] == "satellite" and len(s) > min_hist and all(row[f"r{w}"] is not None for w in wins) and sma is not None
        rows.append(row)

    ranked = [r for r in rows if r["rankable"]]
    n = len(ranked)
    for w in wins:
        order = sorted(ranked, key=lambda r: r[f"r{w}"])
        for i, r in enumerate(order):
            r[f"pct{w}"] = 100.0 * i / (n - 1) if n > 1 else 50.0
    for r in ranked:
        r["score"] = round(sum(r[f"pct{w}"] for w in wins) / len(wins), 2)
    ranked.sort(key=lambda r: -r["score"])
    for i, r in enumerate(ranked, 1):
        r["rank"] = i

    breadth = 100.0 * sum(1 for r in ranked if r["trend_up"]) / n if n else 0.0
    bench = next((r for r in rows if r["id"] == policy["benchmark"]), None)
    ds = policy["defensive_switch"]
    risk_off = bool(bench and bench["trend_up"] is False and breadth < ds["max_breadth_pct"])
    return {"date": d, "rows": rows, "ranked": ranked, "n_ranked": n, "breadth_pct": round(breadth, 1),
            "benchmark_trend_up": bench["trend_up"] if bench else None, "regime": "risk_off" if risk_off else "risk_on"}


# ── Decide ───────────────────────────────────────────────────────────────────
@dataclass
class Decision:
    date: str
    regime: str
    nav_before: float
    targets: dict[str, float]
    trades: list[dict] = field(default_factory=list)
    deferred: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    selected_satellites: list[str] = field(default_factory=list)


def _select_satellites(sc: dict, held: set[str], uni: dict[str, dict], pol: dict) -> tuple[list[dict], list[dict]]:
    """Return (selected rows, exit explanations for held satellites not kept)."""
    sat = pol["satellites"]
    n = sat["count"][sc["regime"]]
    keep_limit = n * sat["hold_buffer_rank_multiple"]
    by_id = {r["id"]: r for r in sc["ranked"]}
    exits = []
    kept = []
    for iid in sorted(held):
        if uni.get(iid, {}).get("sleeve") != "satellite":
            continue
        r = by_id.get(iid)
        if r is None:
            exits.append({"id": iid, "why": "not_rankable", "detail": "insufficient price history to rank"})
        elif not r["trend_up"]:
            exits.append({"id": iid, "why": "trend_down", "detail": f"close {r['close']:.2f} below 200-day average {r['sma200']:.2f}", "rank": r["rank"], "score": r["score"]})
        elif r["rank"] > keep_limit:
            exits.append({"id": iid, "why": "rank_dropped", "detail": f"rank {r['rank']} of {sc['n_ranked']} (keep while ≤ {keep_limit})", "rank": r["rank"], "score": r["score"]})
        else:
            kept.append(r)
    kept.sort(key=lambda r: r["rank"])
    while len(kept) > n:  # risk-off can shrink the slot count
        r = kept.pop()
        exits.append({"id": r["id"], "why": "slots_reduced", "detail": f"{sc['regime']} allows {n} satellites; rank {r['rank']} is the weakest held", "rank": r["rank"], "score": r["score"]})

    def conflicts(r, chosen):
        t = set(r["tags"])
        return any(t & set(c["tags"]) for c in chosen)

    selected = list(kept)
    for r in sc["ranked"]:
        if len(selected) >= n:
            break
        if r["id"] in held or not r["trend_up"] or conflicts(r, selected):
            continue
        selected.append(r)

    # Replacement: full book, best outsider vs weakest keeper.
    if len(kept) == n and kept:
        weakest = max(kept, key=lambda r: r["rank"])
        others = [k for k in kept if k is not weakest]
        for r in sc["ranked"]:
            if r["id"] in held or not r["trend_up"] or conflicts(r, others):
                continue
            if r["score"] >= weakest["score"] + sat["replacement_margin_pts"]:
                selected = others + [r]
                exits.append({"id": weakest["id"], "why": "replaced", "detail": f"{r['id']} scores {r['score']:.0f} vs {weakest['score']:.0f} (margin ≥ {sat['replacement_margin_pts']})", "rank": weakest["rank"], "score": weakest["score"], "replaced_by": r["id"]})
            break
    return selected, exits


def decide(d: str, holdings: dict[str, int], cash: float, prices: Prices, universe: list[dict], policy: dict, sc: dict) -> Decision:
    uni = {i["id"]: i for i in universe}
    px = {iid: prices.close(iid, d) for iid in set(holdings) | set(uni)}
    nav = cash + sum(sh * px[i] for i, sh in holdings.items() if px.get(i))
    regime = sc["regime"]
    held = {i for i, sh in holdings.items() if sh > 0}

    # 1. Target weights ---------------------------------------------------------
    sat = policy["satellites"]
    n = sat["count"][regime]
    selected, sat_exits = _select_satellites(sc, held, uni, policy)
    w_sat = sat["weight_each"]
    targets: dict[str, float] = {r["id"]: w_sat for r in selected}
    cash_t = policy["cash"]["target"]
    defensive = (n - len(selected)) * w_sat
    core_w = 1 - cash_t - w_sat * len(selected) - defensive
    lo, hi = policy["core"]["weight_band"]
    if core_w > hi:
        defensive += core_w - hi
        core_w = hi
    eq_share = policy["core"]["equity_share"][regime]
    targets[policy["core"]["equity"]] = core_w * eq_share
    targets[policy["core"]["bonds"]] = core_w * (1 - eq_share)
    if defensive > 1e-9:
        targets[policy["defensive_switch"]["instrument"]] = targets.get(policy["defensive_switch"]["instrument"], 0) + defensive
    dec = Decision(d, regime, round(nav, 2), {k: round(v, 4) for k, v in targets.items()}, selected_satellites=[r["id"] for r in selected])
    if defensive > 1e-9:
        dec.notes.append(f"{defensive:.0%} parked in {policy['defensive_switch']['instrument']}: "
                         f"{n - len(selected)} of {n} satellite slots unfilled" + (" (risk-off)" if regime == "risk_off" else ""))

    # 2. Instrument changes (entries / full exits), limited per week -------------
    by_id = {r["id"]: r for r in sc["ranked"]}
    exit_info = {e["id"]: e for e in sat_exits}
    changes = []
    for iid in sorted(held):
        if targets.get(iid, 0) <= 0:
            info = exit_info.get(iid) or {"id": iid, "why": "not_in_target", "detail": "not part of the target portfolio (core is " + policy["core"]["equity"] + " + " + policy["core"]["bonds"] + ")"}
            prio = {"trend_down": 0, "not_rankable": 0, "slots_reduced": 1, "replaced": 2, "rank_dropped": 2}.get(info["why"], 3)
            changes.append((prio, "exit", iid, info))
    for iid, w in targets.items():
        if iid not in held and w > 0:
            r = by_id.get(iid)
            info = ({"why": "selected", "detail": f"rank {r['rank']} of {sc['n_ranked']}, score {r['score']:.0f}, uptrend", "rank": r["rank"], "score": r["score"]}
                    if r else {"why": "core_or_defensive", "detail": "core/defensive allocation"})
            changes.append((4 + (r["rank"] / 1000 if r else 0), "entry", iid, info))
    changes.sort(key=lambda c: c[0])
    limit = policy["turnover"]["max_instrument_changes_per_week"]
    allowed, deferred = changes[:limit], changes[limit:]
    for _, kind, iid, info in deferred:
        dec.deferred.append({"id": iid, "kind": kind, **info, "deferred_reason": f"max {limit} instrument changes per week"})
        if kind == "exit":
            targets[iid] = holdings[iid] * px[iid] / nav  # hold as-is this week
        else:
            targets[iid] = 0.0
    change_info = {iid: (kind, info) for _, kind, iid, info in allowed}

    # 3. Orders: sells first, then buys within the cash/deployment budget --------
    bps = policy["execution"]["cost_bps"] / 10_000
    band = policy["turnover"]["rebalance_band_pts"] / 100
    sells, buys = [], []
    # Cash above its band is deployed into underweight holdings even when each
    # holding is individually inside its rebalance band.
    cash_excess = cash / nav > policy["cash"]["band"][1]
    for iid in sorted(set(holdings) | set(targets)):
        p = px.get(iid)
        if not p:
            continue
        cur_w = holdings.get(iid, 0) * p / nav
        tgt_w = targets.get(iid, 0.0)
        diff = tgt_w - cur_w
        kind, info = change_info.get(iid, (None, None))
        if kind is None and abs(diff) <= band and not (diff > 0 and cash_excess and iid in held):
            continue
        if kind is None and iid not in held and tgt_w <= 0:
            continue
        if diff < 0:
            sh = holdings[iid] if tgt_w <= 0 else min(holdings[iid], round(-diff * nav / p))
            if sh > 0:
                sells.append({"id": iid, "side": "sell", "shares": sh, "price": p, "kind": kind or "resize",
                              "reason": info or {"why": "resize", "detail": f"weight {cur_w:.1%} vs target {tgt_w:.1%} (band {band:.0%})"}})
        elif diff > 0:
            buys.append({"id": iid, "side": "buy", "want": diff * nav, "price": p, "kind": kind or "resize",
                         "reason": info or ({"why": "deploy_cash", "detail": f"cash {cash / nav:.1%} above {policy['cash']['band'][1]:.0%} ceiling; topping up toward target {tgt_w:.1%}"}
                                            if abs(diff) <= band else {"why": "resize", "detail": f"weight {cur_w:.1%} vs target {tgt_w:.1%} (band {band:.0%})"})})
    proceeds = 0.0
    for s in sells:
        amt = s["shares"] * s["price"]
        s["amount"] = round(amt, 2)
        s["cost"] = round(amt * bps, 2)
        proceeds += amt - s["cost"]
        dec.trades.append(s)
    cash_after_sells = cash + proceeds
    budget = min(cash_after_sells - cash_t * nav, proceeds + policy["cash"]["max_net_deployment_per_week_pct_nav"] / 100 * nav)
    want = sum(b["want"] for b in buys)
    scale = min(1.0, max(0.0, budget) / want) if want > 0 else 0.0
    if buys and scale < 1:
        dec.notes.append(f"buys scaled to {scale:.0%} of target by the cash/deployment limit")
    for b in sorted(buys, key=lambda b: b["kind"] != "entry"):
        sh = math.floor(b["want"] * scale / (b["price"] * (1 + bps)))
        if sh <= 0:
            continue
        amt = sh * b["price"]
        dec.trades.append({"id": b["id"], "side": "buy", "shares": sh, "price": b["price"], "kind": b["kind"],
                           "amount": round(amt, 2), "cost": round(amt * bps, 2), "reason": b["reason"]})
    dec.targets = {k: round(v, 4) for k, v in targets.items() if v > 0}
    return dec


def apply(holdings: dict[str, int], cash: float, dec: Decision) -> tuple[dict[str, int], float]:
    h = dict(holdings)
    c = cash
    for t in dec.trades:
        if t["side"] == "sell":
            h[t["id"]] -= t["shares"]
            c += t["amount"] - t["cost"]
        else:
            h[t["id"]] = h.get(t["id"], 0) + t["shares"]
            c -= t["amount"] + t["cost"]
    return {k: v for k, v in h.items() if v > 0}, round(c, 2)
