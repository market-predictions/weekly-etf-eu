# Weekly ETF EU Review OS — Next Actions

Current priority: finish WP13G related Codespace validation.

Completed:

```text
WP9
WP10
WP10B
WP11
WP12
WP12B
WP12C
WP12D
WP12E
WP12F
WP13A
WP13B
WP13C
WP13D
WP13E
WP13F
```

WP13G current status:

```text
implemented
selected_next_package=WP13H
selected_next_package_title=explicit authority decision review, review-only
review_chain_complete=true
operational_prerequisites_complete=false
authority_can_be_granted=false
authority_created=false
production_delivery=false
wp13_authority=false
not workflow-integrated
related Codespace validation pending before full closeout
```

Next immediate action:

```text
Run the WP13G focused pytest module.
Run the WP13G focused validator against the committed WP13G artifact.
Run the related WP13A-F review-gate regression tests.
```

Only after these pass should WP13G be marked fully closed.

After WP13G closeout, next selected package:

```text
WP13H — explicit authority decision review, review-only
```

Boundary rule:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
ready_for_wp13_preflight_only=true
wp13_authority=false
```
