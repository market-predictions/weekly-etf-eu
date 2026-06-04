from __future__ import annotations

from decimal import Decimal

from pricing.price_agreement_gate import AgreementGateConfig


def main() -> int:
    config = AgreementGateConfig(max_abs_diff=Decimal("0.01"), max_bps_diff=Decimal("5"))
    if config.min_independent_sources != 2:
        raise SystemExit("invalid min_independent_sources")
    print("PRICE_AGREEMENT_GATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
