# ETF EU Output Contract V1

## Purpose

This contract defines the first non-delivery report output surface for `market-predictions/weekly-etf-eu`.

The output layer must prove that the EU repo can generate clearly separated EU/UCITS report files without using the cloned U.S.-ETF report names or presenting U.S.-listed ETFs as Dutch/EU investable holdings.

## Output filename contract

The EU report output names are:

```text
output/weekly_etf_eu_review_YYMMDD.md
output/weekly_etf_eu_review_nl_YYMMDD.md
```

Future PDF names should be:

```text
output/weekly_etf_eu_review_YYMMDD.pdf
output/weekly_etf_eu_review_nl_YYMMDD.pdf
```

The Dutch report is the primary EU client-facing output. The English report is a companion / operator-facing version during bootstrap.

## Required report wording during bootstrap

Every bootstrap EU report must clearly state:

```text
Current state: cash-only bootstrap
No UCITS holdings funded yet
U.S. ETFs are research proxies only
UCITS candidates require ISIN / KID / trading-line verification
Production delivery is disabled
```

The Dutch report must communicate the same facts in Dutch.

## Prohibited report behavior

The EU report must not:

- use `weekly_analysis_pro_*` filenames for EU output;
- present SPY, QQQ, SMH, GLD, GSG, PPA, PAVE, URNM or other U.S.-listed ETFs as current EU holdings;
- describe U.S. ETFs as fundable Dutch/EU instruments;
- show a portfolio action table with U.S. ETF tickers as investable holdings;
- imply that production delivery has occurred.

## Allowed use of U.S. ETF tickers

U.S. ETF tickers may appear only when explicitly labelled as:

```text
research proxy only
benchmark reference only
not an investable EU holding
```

## Required sections for bootstrap skeleton

The bootstrap skeleton must include:

1. Status / status.
2. Current portfolio state / huidige portefeuillestaat.
3. Investability gate / investeerbaarheidsfilter.
4. Research proxies / onderzoeksproxies.
5. UCITS candidate registry status / status UCITS-register.
6. Next build steps / volgende bouwstappen.
7. Delivery status / leveringsstatus.

## Validator authority

`tools/validate_etf_eu_output_contract.py` is the hard validator for this contract during bootstrap.

A workflow may validate the skeleton and commit generated markdown, but it must not send email or generate production PDFs until later delivery contracts are added and approved.
