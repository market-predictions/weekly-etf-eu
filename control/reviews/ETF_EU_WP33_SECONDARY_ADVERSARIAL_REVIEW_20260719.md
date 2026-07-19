# ETF EU WP33 — Secondary adversarial review

Date: 2026-07-19
Role: independent critical review pass
Mutation authority: none
Status: pending exact-current evidence

## Mandate

Challenge the production integration rather than merely re-reviewing the visual design.

## Required challenges

1. **All-or-nothing mutation:** a failure in either language, render mode or PDF build must leave all four package files unchanged.
2. **Backward compatibility:** disabled and invalid feature states must preserve the existing two-part package.
3. **Dual render contract:** primary HTML must be the inline/table client surface; PDF must use the browser/SVG surface; both must carry identical state facts.
4. **Attachment stability:** the client attachment contract must remain exactly Dutch PDF, English PDF, Dutch HTML and English HTML.
5. **Manifest integrity:** cockpit metadata and internal browser paths must not replace client-file identities or imply new portfolio authority.
6. **Document hierarchy:** cockpit, investor report and analyst report must remain ordered and all fifteen classic sections must remain.
7. **Email degradation:** essential first-page layout and hidden duplicate summary content must survive head-CSS removal.
8. **Replay authority:** the exact-current replay must use the latest accepted normalized EU state and write only to the isolated enablement-preview directory.
9. **Protected state:** portfolio, ledger, scorecard, normalized state and accepted package files must remain unchanged.
10. **Operational scope:** only the routine NO EMAIL generation workflow may enable the flag in WP33; the delivery-only workflow must remain unchanged.
11. **Rollback:** changing the feature value to `disabled` must be sufficient to restore the classic package path.
12. **Future-run boundary:** WP33 must not create or transport a new client report.

## Initial challenge findings

- The existing sender uses the Dutch primary HTML directly as the message body. A separate unused email file would not solve client rendering. The integration was therefore redesigned so primary HTML is the inline/table surface and PDF is rendered from retained browser HTML.
- The resulting HTML and PDF intentionally use different rendering containers. Final review must prove factual identity and document-order identity across both.
- WeasyPrint PDF container bytes may differ across renders even when page images are identical. Final acceptance must use page-render hashes for visual identity and explicit file hashes for the named final artifact.

## Gate

```text
secondary_review_passed=false
exact_current_replay_reviewed=false
production_enablement_recommended=false
```
