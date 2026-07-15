# ETF EU RPT01 Fast-Track Execution Decision

Date: 2026-07-15
Status: adopted

## Decision

Execute `ETF-EU-RPT01_CLIENT_GRADE_REPORT_V2` as one integrated implementation stream with minimal user interaction.

The assistant is authorized to:

- inspect and adapt mature `weekly-etf` donor components;
- create and modify preview-only EU runtime, renderer, validator, workflow and roadmap files;
- trigger the preview through a queue commit;
- inspect and repair concrete implementation failures without requesting permission for each repair;
- update control-state files to reflect actual progress.

The assistant must stop only for:

- a destructive or irreversible production change;
- missing external credentials or unavailable authoritative data that cannot be handled with a truthful fallback;
- live transport or portfolio mutation;
- a final production promotion decision.

## Donor pattern adapted

```text
weekly-etf normalized runtime state
+ macro client surface
+ deterministic equity curve
+ component-based delivery HTML
+ strict but proportionate PDF validation
```

Adaptation rule:

```text
port behavior and presentation architecture
never port U.S. holdings, instrument authority, allocation authority or recipient authority
```

## Implementation boundary

The v2 lane writes only to:

```text
output/client_grade_preview/
output/runtime/etf_eu_client_grade_report_state_*.json
output/quality/etf_eu_client_grade_v2_*.json
```

It does not replace the routine production renderer or delivery workflow.

## Control philosophy

Use a small number of high-value invariants rather than a large sequence of gates:

1. source/state identity is explicit;
2. EU/UCITS authority is preserved;
3. client output is complete and clean;
4. chart behavior is truthful;
5. preview transport is impossible;
6. promotion requires one explicit final decision.

Tests and validators must target likely regressions, not reproduce the full report in assertions.
