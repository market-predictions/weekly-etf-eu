#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

SCHEMA = "etf_eu_client_surface_safety_v1"
CLIENT_KEYS = ("nl_md", "en_md", "nl_html", "en_html", "nl_pdf", "en_pdf")
TEXT_KEYS = ("nl_md", "en_md", "nl_html", "en_html")
STALE_DELIVERY_CLAIMS = (
    "report sent",
    "report delivered",
    "email sent",
    "e-mail verzonden",
    "rapport verzonden",
    "rapport is verzonden",
    "smtp_sendmail_returned_no_exception",
)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _load_donor_proxies(path: Path) -> set[str]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    proxies: set[str] = set()
    for mapping in payload.get("proxy_mappings") or []:
        for ticker in mapping.get("donor_proxies") or []:
            value = str(ticker).strip().upper()
            if value:
                proxies.add(value)
    return proxies


def validate(*, manifest_path: Path, proxy_map_path: Path) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    if manifest.get("schema_version") != "etf_eu_thin_kernel_manifest_v1":
        raise RuntimeError("thin kernel manifest schema mismatch")
    if manifest.get("semantic_state_frozen") is not True:
        raise RuntimeError("thin kernel semantic state is not frozen")
    if manifest.get("post_freeze_semantic_mutation") is not False:
        raise RuntimeError("thin kernel post-freeze mutation contract invalid")

    artifacts = manifest.get("artifacts") or {}
    blockers: list[str] = []
    artifact_evidence: dict[str, dict[str, Any]] = {}
    text_surfaces: dict[str, str] = {}
    for key in CLIENT_KEYS:
        meta = artifacts.get(key)
        if not isinstance(meta, dict):
            blockers.append(f"artifact_missing_from_manifest:{key}")
            continue
        path = Path(str(meta.get("path") or ""))
        if not path.exists():
            blockers.append(f"artifact_missing:{key}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        declared = str(meta.get("sha256") or "").removeprefix("sha256:")
        if actual != declared:
            blockers.append(f"artifact_hash_mismatch:{key}")
        artifact_evidence[key] = {"path": str(path), "sha256": "sha256:" + actual}
        if key in TEXT_KEYS:
            text_surfaces[key] = path.read_text(encoding="utf-8", errors="replace")

    joined = "\n".join(text_surfaces.values())
    folded = joined.casefold()
    stale_delivery_wording_present = any(token.casefold() in folded for token in STALE_DELIVERY_CLAIMS)
    main_surface_tbd_candidate_exposure = re.search(r"\bTBD\b", joined, flags=re.IGNORECASE) is not None
    nan_price_in_client_surface = re.search(r"(?<![A-Za-z])nan(?![A-Za-z])", joined, flags=re.IGNORECASE) is not None

    donor_proxies = _load_donor_proxies(proxy_map_path)
    exposed_proxies = sorted(
        ticker for ticker in donor_proxies
        if re.search(rf"(?<![A-Z0-9]){re.escape(ticker)}(?![A-Z0-9])", joined.upper())
    )
    main_surface_us_proxy_exposure = bool(exposed_proxies)

    flags = {
        "stale_delivery_wording_present": stale_delivery_wording_present,
        "main_surface_us_proxy_exposure": main_surface_us_proxy_exposure,
        "main_surface_tbd_candidate_exposure": main_surface_tbd_candidate_exposure,
        "nan_price_in_client_surface": nan_price_in_client_surface,
    }
    for key, value in flags.items():
        if value:
            blockers.append(key)

    return {
        "schema_version": SCHEMA,
        "status": "PASS" if not blockers else "FAIL",
        "valid": not blockers,
        "thin_kernel_manifest": {"path": str(manifest_path), "sha256": _sha256(manifest_path)},
        "artifacts": artifact_evidence,
        "client_surface_safety": flags,
        "exposed_donor_proxies": exposed_proxies,
        "blockers": blockers,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate frozen ETF EU client surfaces for guarded-delivery safety evidence")
    parser.add_argument("--manifest", default="output/current/manifest.json")
    parser.add_argument("--proxy-map", default="config/ucits_benchmark_proxy_map.yml")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = validate(manifest_path=Path(args.manifest), proxy_map_path=Path(args.proxy_map))
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["valid"]:
        raise SystemExit("ETF_EU_CLIENT_SURFACE_SAFETY_FAILED | " + "; ".join(result["blockers"]))
    print("ETF_EU_CLIENT_SURFACE_SAFETY_PASS")


if __name__ == "__main__":
    main()
