from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise RuntimeError("PyYAML is required for pricing configs. Install with: pip install pyyaml") from exc


class SymbolResolver:
    def __init__(self, registry_file: str | Path):
        self.cfg = yaml.safe_load(Path(registry_file).read_text(encoding="utf-8"))

    def normalize_symbol(self, symbol: str) -> str:
        return symbol.strip().upper()

    def _override(self, symbol: str) -> dict[str, Any]:
        symbol = self.normalize_symbol(symbol)
        return dict(self.cfg.get("overrides", {}).get(symbol, {}) or {})

    def get_source_order(self, symbol: str, kind: str) -> list[str]:
        symbol = self.normalize_symbol(symbol)
        overrides = self.cfg.get("overrides", {})
        defaults = self.cfg["defaults"]

        if kind == "holding":
            order = list(defaults["holding_source_order"])
            if symbol not in overrides:
                order = [x for x in order if x != "issuer_override"]
            return order

        return list(defaults["generic_source_order"])

    def get_issuer_handler(self, symbol: str) -> str | None:
        return self._override(symbol).get("issuer_handler")

    def get_provider_symbol(self, symbol: str, source: str) -> str:
        symbol = self.normalize_symbol(symbol)
        override = self._override(symbol)
        provider_symbols = override.get("provider_symbols") or {}
        if isinstance(provider_symbols, dict):
            provider_symbol = provider_symbols.get(source)
            if provider_symbol:
                return str(provider_symbol).strip()
        return str(override.get("canonical_symbol") or symbol).strip()

    def get_expected_exchange(self, symbol: str) -> str | None:
        value = self._override(symbol).get("expected_exchange")
        return None if value is None else str(value)
