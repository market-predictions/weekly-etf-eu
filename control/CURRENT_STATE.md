# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-19
repository=market-predictions/weekly-etf-eu
main_sha=5cc712582f86a51951cf57c55992f0ddc49a6ff1
state=FRESH_REPORT_CYCLE_OPEN_ON_PRIMARY_VERIFICATION_PRICING
current_report_issue=114
pricing_authority=PRIMARY_CLOSE_PLUS_OPTIONAL_VERIFICATION
pricing_change_issue=111 CLOSED
pricing_change_pr=112 MERGED
pricing_change_merge=5cc712582f86a51951cf57c55992f0ddc49a6ff1
pricing_assurance_issue=113 CLOSED_COMPLETED
principal_decision_required=false
real_broker_execution=false
```

## Current production pricing authority

The prior universal two-live-provider same-date consensus requirement is retired.

Current production semantics are defined by merged PR #112 and summarized canonically in `control/PRICING_AUTHORITY_CURRENT.md`:

- establish source-independent UCITS trading-line identity from the canonical symbol registry;
- require the primary provider symbol to be correctly bound to that exact line;
- one qualified bound provider with the exact requested completed-session close is sufficient for valuation-grade `fresh_exact_unverified` pricing;
- an additional correctly bound exact same-date provider within tolerance upgrades the line to `fresh_exact_verified`;
- a stale, missing or unbound verifier does not invalidate a correctly bound exact primary;
- two accepted exact same-date providers outside tolerance fail closed as `provider_disagreement`;
- stale-only pricing, no exact requested-date close, broken primary binding, returned-symbol mismatch, venue mismatch or currency mismatch remain blocked;
- selected valuation price is the primary provider close, not a median blend.

Any older issue, work-package, metadata or narrative statement saying that every funded line still requires two live providers is historical provenance only and is not current authority.

## Why the rule changed

The 2026-08-17 candidate exposed the liveness defect: Alpha Vantage had exact 2026-08-17 closes for all six funded positions while Yahoo was still on 2026-08-14. The old universal two-provider gate therefore blocked 6/6 valid exact primary closes. PR #112 separated exact primary close authority from independent verification, preserved fail-closed disagreement and identity controls, passed independent assurance, and merged on 2026-08-18.

## Current report lifecycle

Issue #109 is closed as superseded because its body still encoded the retired same-date two-provider requirement. Issue #113 is closed because PR #112 assurance/integration completed. The active fresh-report lineage is issue #114.

The new cycle must:

- use fresh completed-close evidence under the primary+verification pricing authority;
- perform a full current portfolio re-underwrite;
- perform broad donor discovery followed by EU-local UCITS mapping/fundability;
- seek more than six funded positions only where current evidence, fundability, pricing and allocation authority support them; there is no hard ticker-count target;
- preserve whole-share/cash reconciliation;
- produce one normalized NL/EN client-grade artifact set;
- obtain independent exact-head assurance before integration;
- use guarded transport only after separate current send authority;
- claim delivery success only from real receipt/manifest evidence.

## Historical closed cycle

The 2026-08-14 report cycle remains closed and delivery-confirmed. The later email-equity parity repair remains merged and does not reopen that historical cycle.

## Stable boundaries

- no real broker execution;
- no portfolio/share/cash mutation without explicit current allocation authority;
- no diagnostic-only source promotion merely to increase coverage;
- pricing confidence is not an allocation rule;
- candidate generation has no SMTP/delivery authority;
- no delivery-success claim without positive receipt/manifest evidence;
- prior reports and old issues are historical context, not current pricing truth.
