from __future__ import annotations

import sys
from pathlib import Path


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pricing.build_etf_eu_allocator_market_evidence_v3 import main


if __name__ == "__main__":
    main()
