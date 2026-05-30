from __future__ import annotations

import re
from html import unescape
from typing import Any

DEFAULT_MAX_POSITION_PCT = 25.0
TAG_RE = re.compile(r"<[^>]+>")
TR_RE = re.compile(r"<tr\b[^>]*>.*?</tr>", re.DOTALL | re.IGNORECASE)
TD_RE = re.compile(r"<td\b[^>]*>.*?</td>", re.DOTALL | re.IGNORECASE)
TH_RE = re.compile(r"<th\b[^>]*>.*?</th>", re.DOTALL | re.IGNORECASE)
ROTATION_TABLE_RE = re.compile(r"<table\b(?=[^>]*\brotation-plan-table\b)[^>]*>.*?</table>", re.DOTALL | re.IGNORECASE)
ACTION_ROW_RE = re.compile(
    r"(<tr\b[^>]*>\s*<th\b[^>]*>\s*(?:Add / destination|Add|Toevoegen / bestemming|Toevoegen)\s*</th>\s*<td\b[^>]*>)(.*?)(</td>\s*</tr>)",
    re.DOTALL | re.IGNORECASE,
)
SENTENCE_RE = re.compile(r"[^.!?\n]+[.!?]?", re.MULTILINE)
OVER_CAP_OK_MARKERS = [
    "no fresh capital",
    "above the 25% max-position cap",
    "above 25% cap",
    "above cap",
    "capped in the current portfolio",
    "geen nieuw kapitaal",
    "boven de 25%-limiet",
]
OVER_CAP_FORBIDDEN_PHRASES = [
    "leading funded growth exposure",
    "candidate for additional capital",
    "first candidate for additional capital",
    "Actionable now",
]


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _plain(html: str) -> str:
    return re.sub(r"\s+", " ", unescape(TAG_RE.sub(" ", html))).strip()


def _is_ok_cap_context(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in OVER_CAP_OK_MARKERS)


def position_weights(state: dict[str, Any]) -> dict[str, float]:
    positions = state.get("positions") or []
    nav = _float((state.get("portfolio") or {}).get("total_portfolio_value_eur"))
    if nav <= 0:
        nav = sum(_float(p.get("market_value_eur") or p.get("previous_market_value_eur")) for p in positions) + _float((state.get("portfolio") or {}).get("cash_eur"))
    weights: dict[str, float] = {}
    for position in positions:
        ticker = str(position.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        weight = _float(position.get("current_weight_pct"), -1.0)
        if weight < 0:
            weight = _float(position.get("previous_weight_pct"), -1.0)
        if weight < 0 and nav > 0:
            weight = _float(position.get("market_value_eur") or position.get("previous_market_value_eur")) / nav * 100.0
        weights[ticker] = round(weight, 2)
    return weights


def over_cap_tickers(state: dict[str, Any], max_position_pct: float = DEFAULT_MAX_POSITION_PCT) -> list[str]:
    return sorted(ticker for ticker, weight in position_weights(state).items() if weight > max_position_pct)


def _contains_ticker(html_fragment: str, ticker: str) -> bool:
    return bool(re.search(rf"(?:>|\b){re.escape(ticker)}(?:<|\b)", html_fragment, flags=re.IGNORECASE))


def _remove_ticker_from_cell(cell_html: str, ticker: str, empty_label: str) -> str:
    updated = re.sub(rf"\s*,?\s*<a\b[^>]*>\s*{re.escape(ticker)}\s*</a>\s*,?\s*", " ", cell_html, flags=re.IGNORECASE)
    updated = re.sub(rf"\s*,?\s*\b{re.escape(ticker)}\b\s*,?\s*", " ", updated, flags=re.IGNORECASE)
    updated = re.sub(r"\s*,\s*,\s*", ", ", updated)
    updated = re.sub(r"^\s*,\s*|\s*,\s*$", "", updated.strip())
    if not _plain(updated) or _plain(updated).lower() in {"none", "geen"}:
        return empty_label
    return updated


def _no_fresh_cash_label(language: str = "en") -> str:
    if language == "nl":
        return "Aanhouden / geen nieuw kapitaal boven 25%-limiet"
    return "Hold / no fresh cash while above 25% cap"


def _capped_actionable_label(language: str = "en") -> str:
    if language == "nl":
        return "Structureel kansrijk, maar geen nieuw kapitaal boven de 25%-limiet"
    return "Structurally actionable, but no fresh capital while above cap"


def _none_label(language: str = "en") -> str:
    return "Geen" if language == "nl" else "None"


def _sanitize_action_rows(html: str, tickers: list[str], language: str) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, cell, suffix = match.groups()
        updated_cell = cell
        for ticker in tickers:
            if _contains_ticker(updated_cell, ticker):
                updated_cell = _remove_ticker_from_cell(updated_cell, ticker, _none_label(language))
        return prefix + updated_cell + suffix
    return ACTION_ROW_RE.sub(repl, html)


def _sanitize_rotation_plan_tables(html: str, tickers: list[str], language: str) -> str:
    def table_repl(match: re.Match[str]) -> str:
        table = match.group(0)
        rows = list(TR_RE.finditer(table))
        if not rows:
            return table
        updated = table
        for row_match in reversed(rows):
            row = row_match.group(0)
            cells = list(TD_RE.finditer(row))
            if len(cells) < 5:
                continue
            # Post-execution table columns: Close, Reduce, Hold, Add, Replace.
            # Pre-execution table columns: Close, Reduce, Hold, Hold override, Add/destination, Replace.
            add_index = 4 if len(cells) >= 6 else 3
            cell_match = cells[add_index]
            cell = cell_match.group(0)
            new_cell = cell
            for ticker in tickers:
                if _contains_ticker(new_cell, ticker):
                    inner = re.sub(r"^<td\b[^>]*>|</td>$", "", new_cell, flags=re.DOTALL | re.IGNORECASE)
                    inner = _remove_ticker_from_cell(inner, ticker, _none_label(language))
                    new_cell = re.sub(r">.*<", f">{inner}<", new_cell, count=1, flags=re.DOTALL)
            if new_cell != cell:
                new_row = row[:cell_match.start()] + new_cell + row[cell_match.end():]
                updated = updated[:row_match.start()] + new_row + updated[row_match.end():]
        return updated
    return ROTATION_TABLE_RE.sub(table_repl, html)


def _sanitize_ticker_rows(html: str, tickers: list[str], language: str) -> str:
    replacement = _no_fresh_cash_label(language)
    def repl(match: re.Match[str]) -> str:
        row = match.group(0)
        if not any(_contains_ticker(row, ticker) for ticker in tickers):
            return row
        row = re.sub(r">\s*Add\s*<", f">{replacement}<", row)
        row = re.sub(r">\s*Toevoegen\s*<", f">{replacement}<", row)
        return row
    return TR_RE.sub(repl, html)


def _sanitize_over_cap_actionable_rows(html: str, tickers: list[str], language: str) -> str:
    replacement = _capped_actionable_label(language)
    def repl(match: re.Match[str]) -> str:
        row = match.group(0)
        if any(_contains_ticker(row, ticker) for ticker in tickers):
            row = re.sub(r">\s*Actionable now\s*<", f">{replacement}<", row, flags=re.IGNORECASE)
            row = re.sub(r"\bActionable now\b", replacement, row, flags=re.IGNORECASE)
        return row
    return TR_RE.sub(repl, html)


def _replace_ticker_sentence(html: str, ticker: str, phrase_pattern: str, replacement_tail: str) -> str:
    ticker_expr = rf"(?P<ticker>(?:<a\b[^>]*>\s*{re.escape(ticker)}\s*</a>|\b{re.escape(ticker)}\b))"
    pattern = re.compile(ticker_expr + phrase_pattern, flags=re.IGNORECASE)
    return pattern.sub(lambda m: f"{m.group('ticker')}{replacement_tail}", html)


def _sanitize_best_opportunity_copy(html: str, tickers: list[str]) -> str:
    for ticker in tickers:
        replacement_tail = " remains the best earned exposure, but no fresh capital is added while it is above the 25% max-position cap."
        html = _replace_ticker_sentence(
            html,
            ticker,
            r"\s+remains the leading funded growth exposure,\s+subject to the max-position rule\.",
            replacement_tail,
        )
        html = _replace_ticker_sentence(
            html,
            ticker,
            r"\s+remains the first candidate for additional capital only if the 25% position-size rule leaves room\.",
            replacement_tail,
        )
        html = _replace_ticker_sentence(
            html,
            ticker,
            r"\s+is a candidate for additional capital[^\.]*\.",
            replacement_tail,
        )
    return html


def sanitize_over_cap_add_html(html: str, state: dict[str, Any], *, max_position_pct: float = DEFAULT_MAX_POSITION_PCT, language: str = "en") -> str:
    tickers = over_cap_tickers(state, max_position_pct=max_position_pct)
    if not tickers:
        return html
    html = _sanitize_action_rows(html, tickers, language)
    html = _sanitize_rotation_plan_tables(html, tickers, language)
    html = _sanitize_ticker_rows(html, tickers, language)
    html = _sanitize_over_cap_actionable_rows(html, tickers, language)
    html = _sanitize_best_opportunity_copy(html, tickers)
    return html


def _violating_sentences(text: str, ticker: str) -> list[str]:
    failures: list[str] = []
    for sentence_match in SENTENCE_RE.finditer(text):
        sentence = sentence_match.group(0).strip()
        if not re.search(rf"\b{re.escape(ticker)}\b", sentence, flags=re.IGNORECASE):
            continue
        lower = sentence.lower()
        if any(phrase.lower() in lower for phrase in OVER_CAP_FORBIDDEN_PHRASES) and not _is_ok_cap_context(sentence):
            failures.append(sentence)
    return failures


def _violating_rows(html: str, ticker: str) -> list[str]:
    failures: list[str] = []
    for row_match in TR_RE.finditer(html):
        row = row_match.group(0)
        if not _contains_ticker(row, ticker):
            continue
        row_text = _plain(row)
        lower = row_text.lower()
        if "actionable now" in lower and not _is_ok_cap_context(row_text):
            failures.append(row_text)
    return failures


def validate_no_over_cap_add_html(html: str, state: dict[str, Any], *, report_name: str, max_position_pct: float = DEFAULT_MAX_POSITION_PCT) -> None:
    tickers = over_cap_tickers(state, max_position_pct=max_position_pct)
    if not tickers:
        return
    text = _plain(html)
    failures: list[str] = []
    for ticker in tickers:
        patterns = [
            rf"Add / destination\s+{re.escape(ticker)}\b",
            rf"\bAdd\s+{re.escape(ticker)}\b",
            rf"\b{re.escape(ticker)}\s+Add\b",
            rf"Toevoegen / bestemming\s+{re.escape(ticker)}\b",
            rf"\b{re.escape(ticker)}\s+Toevoegen\b",
        ]
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns):
            failures.append(f"{ticker}:shown_as_add")
        for sentence in _violating_sentences(text, ticker):
            failures.append(f"{ticker}:forbidden_phrase:{sentence[:160]}")
        for row in _violating_rows(html, ticker):
            failures.append(f"{ticker}:actionable_now_row:{row[:160]}")
    if failures:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: over-cap actionability wording violates max-position cap {max_position_pct:.2f}%: "
            + "; ".join(sorted(set(failures)))
        )
