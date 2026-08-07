# PR #80 exact-head validation reactivation

Date: 2026-08-08 Europe/Amsterdam
Repository: `market-predictions/weekly-etf-eu`
PR: #80
Role: `implementation_operations`

## Purpose

Re-enter the existing product-boundary and allocation-lineage validation path after the candidate head changed during cleanup of obsolete one-shot workflow machinery.

This note changes no portfolio, pricing, report, allocation, renderer, transport or delivery behavior. It exists only to create a normal GitHub contents commit / pull-request synchronize event so the existing read-only PR validation workflows can evaluate the exact current candidate.

The stacked PR base branch originally lacked `.github/workflows/validate-etf-eu-repository-boundary.yml`. Control restored that existing read-only gate to the base branch before this retry so GitHub can resolve the `pull_request` workflow from the actual target branch.

## Required next evidence

- `Validate Weekly ETF EU product boundary` on the exact new PR head;
- fresh governed ETF EU candidate workflow on the exact new PR head where its existing PR path contract applies;
- no report send, portfolio mutation, ledger mutation or broker execution;
- any failure is routed back to implementation with raw job evidence.
