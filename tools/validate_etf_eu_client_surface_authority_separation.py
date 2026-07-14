from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUTHORITY_TOKENS = [
    "ready_for_controlled_delivery=",
    "send_executed=",
    "transport_attempted=",
    "receipt_confirmed=",
    "valuation_grade=",
    "funding_authority=",
    "portfolio_mutation=",
    "production_delivery_authority=",
    "Authority flags",
]


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing internal authority artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _pdf_text(path: Path) -> str:
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext is required")
    completed = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, text=True, capture_output=True)
    return completed.stdout


def _absent(paths: list[Path], *, pdf: bool = False) -> bool:
    text = "\n".join(_pdf_text(path) if pdf else path.read_text(encoding="utf-8") for path in paths)
    lowered = text.casefold()
    return not any(token.casefold() in lowered for token in AUTHORITY_TOKENS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU authority evidence separation from client outputs.")
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--sanitization-run-id", required=True)
    parser.add_argument("--internal-artifact", action="append", required=True)
    parser.add_argument("--markdown", action="append", required=True)
    parser.add_argument("--html", action="append", required=True)
    parser.add_argument("--pdf", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    internal_paths = [Path(value) for value in args.internal_artifact]
    markdown_paths = [Path(value) for value in args.markdown]
    html_paths = [Path(value) for value in args.html]
    pdf_paths = [Path(value) for value in args.pdf]
    internal_payloads = [_load(path) for path in internal_paths]
    authority_flags_preserved = any(
        any(key in payload for key in ("valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"))
        for payload in internal_payloads
    )
    md_absent = _absent(markdown_paths)
    html_absent = _absent(html_paths)
    pdf_absent = _absent(pdf_paths, pdf=True)
    blockers: list[str] = []
    if not authority_flags_preserved:
        blockers.append("Authority flags were not found in internal evidence")
    if not md_absent:
        blockers.append("Authority metadata remains in client Markdown")
    if not html_absent:
        blockers.append("Authority metadata remains in client HTML")
    if not pdf_absent:
        blockers.append("Authority metadata remains in client PDF")

    payload = {
        "schema_version": "etf_eu_client_surface_authority_separation_v1",
        "artifact_type": "etf_eu_client_surface_authority_separation",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_run_id": args.source_run_id,
        "sanitization_run_id": args.sanitization_run_id,
        "internal_authority_source_artifacts": [str(path) for path in internal_paths],
        "client_markdown_paths": [str(path) for path in markdown_paths],
        "client_html_paths": [str(path) for path in html_paths],
        "client_pdf_paths": [str(path) for path in pdf_paths],
        "authority_flags_preserved_in_internal_evidence": authority_flags_preserved,
        "authority_flags_absent_from_client_markdown": md_absent,
        "authority_flags_absent_from_client_html": html_absent,
        "authority_flags_absent_from_client_pdf": pdf_absent,
        "separation_gate_passed": not blockers,
        "blockers": blockers,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["separation_gate_passed"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
