# ETF EU Discovery-to-Fundability Contract V1

Date: 2026-08-10
Status: CANONICAL

## Purpose
Weekly ETF EU should inherit the donor's broad discovery behavior without importing U.S.-listed ETFs as investable instruments.

## Canonical chain
```text
donor broad lane assessment
→ donor primary/alternative research proxies
→ EU proxy-to-UCITS mapping
→ ISIN/exact-line/KID verification
→ same-date completed-close pricing
→ current recommendation/re-underwriting review
→ explicit allocation decision
→ protected model-state mutation (separately governed)
```

No earlier step may imply funding authority.

## Breadth contract
The EU run must assess the donor breadth buckets when they exist in the donor artifact, including at least:
- ai/digital infrastructure
- defense/resilience
- grid/power/electrification
- uranium/nuclear
- agriculture/food security
- water
- China
- India/regional industrialization
- biotech/healthcare
- fintech/financial infrastructure
- robotics/automation
- critical minerals/materials

A bucket may remain `mapping_required` or `pricing_required`; breadth assessment is not equivalent to fundability.

## Mapping authority
`config/ucits_benchmark_proxy_map.yml` is the mapping layer. It must never contain current portfolio quantities or imply funding.

Each mapped candidate must expose:
```text
exposure_id
proxy set
ISIN
fund name
exact trading line or explicit unresolved status
UCITS/KID identity status
mapping status
```

## Fundability states
Allowed normalized states:
```text
FUNDED_MODEL_POSITION
FUNDABLE_REQUIRES_ALLOCATION_DECISION
PRICED_BUT_REUNDERWRITING_INCOMPLETE
IDENTITY_OR_KID_INCOMPLETE
PRICING_REQUIRED
MAPPING_REQUIRED
POLICY_BLOCKED
RESEARCH_ONLY
```

## Donor parity
Port from donor:
- broad assessment before publication;
- challengers and novelty;
- current relative-strength/liquidity evidence where available;
- direct alternative comparison;
- cash deployment discipline;
- recommendation memory.

Do not port:
- U.S. ticker funding authority;
- U.S. broker/exchange assumptions;
- U.S. state/recipients/delivery settings.

## Output requirement
The client report may show only a concise radar. The run-scoped normalized state must preserve the larger assessed universe and disclose why omitted candidates are not currently fundable.
