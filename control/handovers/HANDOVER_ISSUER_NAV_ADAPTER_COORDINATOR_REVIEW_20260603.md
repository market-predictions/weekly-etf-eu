# Coordinator Review — Issuer NAV Adapter Draft

Date: 2026-06-03  
Branch reviewed: `workstream/issuer-nav-adapter`

## Status

```text
reviewed_as_interface_based_draft_not_integrated
```

## Coordinator verdict

The issuer NAV/reference adapter is a valid draft and is closer to final integration shape than the other adapter drafts because it already implements the shared pricing-interface shape from `workstream/pricing-interface`.

It should still not be merged before the common pricing interface lands in `main`.

Reason:

- the branch includes the full pricing-interface file set plus the issuer NAV adapter files;
- the pricing-interface PR is not integrated into `main` yet;
- this branch is diverged from current `main`;
- issuer NAV must remain reference/stale-check evidence, not exchange trading-line close authority.

## Files observed in branch scope

The branch currently includes inherited pricing-interface files:

```text
pricing/README.md
pricing/price_result_schema.py
pricing/source_selection.py
pricing/sources/__init__.py
pricing/sources/base.py
tests/fixtures/pricing/fake_price_rows.json
tests/test_pricing_interface.py
```

And issuer NAV adapter files:

```text
pricing/sources/issuer_nav.py
tests/fixtures/pricing/issuer_nav/missing_currency_nav.json
tests/fixtures/pricing/issuer_nav/valid_cspx_nav.json
tests/test_issuer_nav_adapter.py
```

## Valid aspects

- Adapter implements `PriceSource.fetch_eod_close(request) -> PriceResult`.
- Adapter uses shared `PriceRequest`, `PriceResult`, `SourceLineage`, and shared status constants.
- Adapter supports inline `issuer_nav_data` and local `issuer_nav_path`.
- Adapter explicitly marks evidence as `value_type=issuer_nav_reference`.
- Adapter records `not_exchange_trading_line_close=True` in raw evidence.
- Adapter uses:

```text
license_class=issuer_public
authority_tier=diagnostic_candidate_source
```

- Adapter has fixture-only tests and no live network calls.
- Adapter preserves safety boundaries through `PriceResult.as_dict()`:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
```

## Integration blockers before merge

1. Merge the common pricing interface PR first.
2. Rebase or refresh `workstream/issuer-nav-adapter` onto the final pricing-interface head or current `main` after interface integration.
3. Ensure the final issuer branch diff only contains issuer NAV adapter/test/fixture files, not duplicate pricing-interface files.
4. Rerun:

```text
python -m pytest tests/test_issuer_nav_adapter.py -q
```

5. Confirm `4 passed` after rebase.
6. Keep issuer NAV separate from valuation-grade market close authority.
7. Do not wire issuer NAV into valuation artifact builder, source selection, agreement gate, workflow, output, PDF, email, or state mutation in this branch.

## Reported validation

```text
python -m pytest tests/test_issuer_nav_adapter.py -q
4 passed
```

## No integration performed

No merge was performed. No valuation builder, validator, workflow, output, state, PDF, email, delivery or control-state behavior was changed by this review.
