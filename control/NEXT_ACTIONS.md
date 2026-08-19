# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
FRESH_REPORT_CYCLE_114_ACTIVE
pricing_authority=PRIMARY_CLOSE_PLUS_OPTIONAL_VERIFICATION
```

The active production lineage is issue #114. Issue #109 is superseded and closed; its old same-date two-provider requirement is historical only. PR #112 is merged and is the current pricing baseline.

## Current pricing gate for the fresh cycle

Use `control/PRICING_AUTHORITY_CURRENT.md` as the human-readable current pricing summary and live merged runtime/tests as executable authority.

For each exact UCITS trading line:

- one qualified, correctly bound provider with the exact requested completed-session close is sufficient for valuation-grade `fresh_exact_unverified` pricing;
- a second correctly bound exact same-date provider within tolerance upgrades the line to `fresh_exact_verified`;
- a stale/missing/unbound verifier does not block a correctly bound exact primary;
- actual same-date disagreement outside tolerance fails closed;
- stale-only/no-exact-close/identity or primary-binding mismatch remains blocked.

Do **not** resurrect the retired rule that every funded line requires two simultaneous live providers.

## Fresh report cycle #114

The current cycle must:

- resolve the latest applicable completed-close date from fresh evidence;
- perform a full portfolio re-underwrite;
- run broad discovery, then EU-local UCITS identity/investability/fundability checks;
- try to achieve more than six funded positions where evidence supports this, without a hard position-count target or relaxed fundability/pricing standards;
- use whole shares and reconcile residual cash exactly;
- render NL primary + EN companion from one normalized state;
- use the current deterministic PNG equity-curve contract for HTML/PDF/email parity;
- pass machine, arithmetic and client-grade/visual QA;
- freeze one exact candidate for independent assurance;
- merge only after independent exact-head PASS and governed integration authority;
- use guarded transport only after separate current guarded-send authority;
- claim delivery success only from real recipient/receipt/attachment evidence or equivalent positive manifest.

## Protected boundaries

- no real broker execution;
- no share/cash mutation without explicit current allocation authority;
- no hard ticker-count target;
- no retired 50%/35%/15% allocation rules;
- no diagnostic-only source promotion to force coverage;
- no stale historical price treated as current truth;
- candidate generation has no SMTP/delivery authority;
- no rerender after artifact approval;
- no delivery-success claim without positive receipt/manifest evidence.

## Controller housekeeping

Read-first narrative state was stale after PR #112. Issue #115 exists specifically to reconcile canonical documentation so old two-provider wording cannot silently override live merged pricing behavior again. Historical issues/work packages remain provenance and must be interpreted by date and lifecycle state, not as current authority.
