# ETF EU Cockpit - Multi-line Pricing Preview

## Wat dit nu bewijst

De cockpit kan nu een multi-line pricing structuur tonen zonder U.S. proxyprijzen of handmatige koersen te gebruiken.

De multi-line structuur staat klaar, maar alleen SXR8.DE is nu succesvol geprijsd. Extra regels blijven expliciet pending of failed totdat provider- en registry-bewijs slagen.

## Koerstabel - verified EU lines

| ISIN | Fonds | Handelslijn | Valuta | Slotdatum | Slotkoers | Bron | Status |
|---|---|---|---|---:|---:|---|---|
| IE00B5BMR087 | iShares Core S&P 500 UCITS ETF USD (Acc) | SXR8.DE | EUR | 2026-07-03 | 706.119995 | yahoo_chart_v8 | success |

## Niet opgenomen / nog niet geprijsd

| ISIN | Fonds | Handelslijn | Status | Reden |
|---|---|---|---|---|
| IE00B5BMR087 | iShares Core S&P 500 UCITS ETF USD (Acc) | CSPX.L | skipped_pending_registry_status | registry line exists but pricing_status remains pending_pipeline_test; no committed provider close in this package |
| IE00BMC38736 | VanEck Semiconductor UCITS ETF | pending_verification | skipped_pending_registry_status | pricing_symbol_yahoo is pending_verification and exchange line is not yet verified |

## Wat dit nog niet bewijst

Dit is een beperkte multi-line koerspreview. Dit is geen waarderingsgeschikte prijsbasis, geen client-grade rapportbewijs en geen leveringsautorisatie.

Het bewijst geen funding, portefeuillemutatie, kandidaatpromotie of productiepad.

## Volgende stap

ETF-EU-WP15AA-FIX - repareer registry/provider-dekking zodat de preview minimaal twee succesvol geprijsde verified EU trading lines kan tonen.
