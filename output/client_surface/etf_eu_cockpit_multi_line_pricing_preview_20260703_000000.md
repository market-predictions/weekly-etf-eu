# ETF EU Cockpit - Multi-line Pricing Preview

## Wat dit nu bewijst

De cockpit kan nu minimaal twee EU trading lines tonen met echte provider-slotkoersen, zonder U.S. proxyprijzen of handmatige koersen te gebruiken.

## Koerstabel - verified EU lines

| ISIN | Fonds | Handelslijn | Valuta | Slotdatum | Slotkoers | Bron | Status |
|---|---|---|---|---:|---:|---|---|
| IE00B5BMR087 | iShares Core S&P 500 UCITS ETF USD (Acc) | SXR8.DE | EUR | 2026-07-03 | 706.119995 | yahoo_chart_v8 | success |
| IE00B5BMR087 | iShares Core S&P 500 UCITS ETF USD (Acc) | CSPX.L | USD | 2026-07-03 | 807.859985 | yahoo_chart_v8 | success |

## Niet opgenomen / nog niet geprijsd

| ISIN | Fonds | Handelslijn | Status | Reden |
|---|---|---|---|---|
| IE00BMC38736 | VanEck Semiconductor UCITS ETF | pending_verification | skipped_pending_registry_status | pricing_symbol_yahoo is pending_verification and exchange line is not yet verified |

## Wat dit nog niet bewijst

Dit is een beperkte multi-line koerspreview. Dit is geen waarderingsgeschikte prijsbasis, geen client-grade rapportbewijs en geen leveringsautorisatie.

Het bewijst geen funding, portefeuillemutatie, kandidaatpromotie of productiepad.

## Volgende stap

ETF-EU-WP15AB - render de gerepareerde multi-line pricing preview naar een PDF-style cockpit candidate en voer een visuele review checkpoint uit zonder levering.
