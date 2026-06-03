from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from pricing.price_result_schema import (
    AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE,
    LICENSE_ISSUER_PUBLIC,
    STATUS_UNRESOLVED_NO_DATA,
    STATUS_UNRESOLVED_NOT_CONFIGURED,
    STATUS_UNRESOLVED_PROVIDER_ERROR,
    PriceResult,
    SourceLineage,
)
from pricing.sources.base import PriceRequest, PriceSource


class IssuerNavSource(PriceSource):
    """Fixture/file-backed issuer NAV/reference adapter.

    Issuer NAV is deliberately modelled as reference evidence, not as an
    exchange trading-line close. The adapter therefore uses the common typed
    PriceResult shape but marks lineage as diagnostic candidate evidence and
    preserves ``value_type=issuer_nav_reference`` in raw evidence.

    No live network calls are performed here. Runtime integrations can supply
    either ``provider_config['issuer_nav_data']`` or
    ``provider_config['issuer_nav_path']``.
    """

    source_id = "issuer_nav_reference"
    provider_name = "Issuer NAV Reference"
    license_class = LICENSE_ISSUER_PUBLIC
    authority_tier = AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE

    def fetch_eod_close(self, request: PriceRequest) -> PriceResult:
        lineage_base = {
            "source_id": self.source_id,
            "provider_name": self.provider_name,
            "license_class": self.license_class,
            "authority_tier": self.authority_tier,
        }
        config = request.provider_config or {}
        data, evidence_path, load_errors = self._load_payload(config)
        if load_errors:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_NOT_CONFIGURED if "missing_issuer_nav_input" in load_errors else STATUS_UNRESOLVED_PROVIDER_ERROR,
                errors=load_errors,
                raw_evidence_path=evidence_path,
                raw_evidence={"value_type": "issuer_nav_reference", "load_errors": load_errors},
            )

        row, selection_errors = self._select_row(data, request)
        if selection_errors:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=selection_errors,
                raw_evidence_path=evidence_path,
                raw_evidence={"value_type": "issuer_nav_reference", "payload_summary": self._payload_summary(data)},
            )

        assert row is not None
        validation_errors = self._validate_row(row, request)
        raw_evidence = {
            "value_type": "issuer_nav_reference",
            "not_exchange_trading_line_close": True,
            "selected_row": row,
        }
        if validation_errors:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=validation_errors,
                raw_evidence_path=evidence_path,
                raw_evidence=raw_evidence,
            )

        lineage = SourceLineage.now(
            **lineage_base,
            raw_evidence_path=evidence_path,
            raw_evidence=raw_evidence,
        )
        return PriceResult.observed(
            identity=request.identity,
            lineage=lineage,
            observed_date=str(row["nav_date"]),
            close=Decimal(str(row["nav"])),
            currency=str(row["currency"]).upper(),
        )

    def _unresolved(
        self,
        request: PriceRequest,
        *,
        status: str,
        errors: list[str],
        raw_evidence_path: str | None,
        raw_evidence: dict[str, Any],
    ) -> PriceResult:
        return PriceResult.unresolved(
            identity=request.identity,
            lineage=SourceLineage.now(
                source_id=self.source_id,
                provider_name=self.provider_name,
                license_class=self.license_class,
                authority_tier=self.authority_tier,
                raw_evidence_path=raw_evidence_path,
                raw_evidence=raw_evidence,
            ),
            status=status,
            errors=errors,
        )

    def _load_payload(self, config: dict[str, Any]) -> tuple[dict[str, Any] | list[Any] | None, str | None, list[str]]:
        if "issuer_nav_data" in config:
            data = config["issuer_nav_data"]
            if isinstance(data, (dict, list)):
                return data, None, []
            return None, None, ["issuer_nav_data_must_be_dict_or_list"]

        path_value = config.get("issuer_nav_path")
        if not path_value:
            return None, None, ["missing_issuer_nav_input"]

        path = Path(str(path_value))
        try:
            return json.loads(path.read_text(encoding="utf-8")), str(path), []
        except FileNotFoundError:
            return None, str(path), [f"issuer_nav_file_not_found:{path}"]
        except json.JSONDecodeError as exc:
            return None, str(path), [f"issuer_nav_json_parse_error:{exc.msg}"]

    def _select_row(self, data: dict[str, Any] | list[Any] | None, request: PriceRequest) -> tuple[dict[str, Any] | None, list[str]]:
        if data is None:
            return None, ["issuer_nav_payload_missing"]
        rows: list[Any]
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            rows = data["rows"]
        elif isinstance(data, list):
            rows = data
        elif isinstance(data, dict):
            rows = [data]
        else:
            return None, ["issuer_nav_payload_must_be_object_or_rows_array"]

        candidates = [row for row in rows if isinstance(row, dict)]
        if not candidates:
            return None, ["issuer_nav_rows_empty_or_invalid"]

        exact_identity = [
            row
            for row in candidates
            if str(row.get("isin", "")).upper() == request.identity.isin.upper()
            and str(row.get("exchange_ticker", "")).upper() == request.identity.exchange_ticker.upper()
        ]
        if exact_identity:
            candidates = exact_identity
        else:
            by_isin = [row for row in candidates if str(row.get("isin", "")).upper() == request.identity.isin.upper()]
            if by_isin:
                candidates = by_isin

        if request.requested_date:
            dated = [row for row in candidates if str(row.get("nav_date")) == request.requested_date]
            if not dated:
                return None, [f"issuer_nav_missing_requested_date:{request.requested_date}"]
            candidates = dated

        candidates = sorted(candidates, key=lambda row: str(row.get("nav_date", "")), reverse=True)
        return candidates[0], []

    def _validate_row(self, row: dict[str, Any], request: PriceRequest) -> list[str]:
        errors: list[str] = []
        if not row.get("nav"):
            errors.append("issuer_nav_missing_nav")
        else:
            try:
                nav = Decimal(str(row["nav"]))
                if nav <= 0:
                    errors.append("issuer_nav_must_be_positive")
            except (InvalidOperation, ValueError):
                errors.append("issuer_nav_parse_error")

        nav_date = row.get("nav_date")
        if not nav_date:
            errors.append("issuer_nav_missing_date")
        else:
            try:
                date.fromisoformat(str(nav_date))
            except ValueError:
                errors.append("issuer_nav_date_not_iso")

        currency = str(row.get("currency", "")).upper()
        if not currency:
            errors.append("issuer_nav_missing_currency")
        elif currency != request.identity.trading_currency.upper():
            errors.append(f"issuer_nav_currency_mismatch:{currency}!={request.identity.trading_currency.upper()}")

        return errors

    def _payload_summary(self, data: dict[str, Any] | list[Any] | None) -> dict[str, Any]:
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            return {"shape": "object_with_rows", "row_count": len(data["rows"])}
        if isinstance(data, list):
            return {"shape": "rows_array", "row_count": len(data)}
        if isinstance(data, dict):
            return {"shape": "single_object", "keys": sorted(data.keys())}
        return {"shape": type(data).__name__}
