#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import PurePosixPath
from typing import Any

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
REQUIRED_ARTIFACT_KEYS = ("nl_md", "en_md", "nl_html", "en_html", "nl_pdf", "en_pdf")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _load_json_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssertionError(f"invalid JSON for {label}") from exc
    _require(isinstance(payload, dict), f"JSON object required for {label}")
    return payload


def _normalise_hash(value: str) -> str:
    value = value.lower()
    return value if value.startswith("sha256:") else "sha256:" + value


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise AssertionError(f"git command failed: {' '.join(args)}: {detail}")
    return result


def _require_commit(sha: str, label: str) -> None:
    _require(SHA_RE.fullmatch(sha) is not None, f"invalid {label} sha")
    result = _git(["cat-file", "-e", f"{sha}^{{commit}}"], check=False)
    _require(result.returncode == 0, f"{label} does not resolve to a Git commit")


def _require_ancestor(ancestor: str, descendant: str, message: str) -> None:
    result = _git(["merge-base", "--is-ancestor", ancestor, descendant], check=False)
    _require(result.returncode == 0, message)


def _repo_path(value: object, label: str) -> str:
    raw = str(value or "")
    path = PurePosixPath(raw)
    _require(raw and not path.is_absolute(), f"{label} must be repository-relative")
    _require(".." not in path.parts, f"{label} may not escape repository")
    _require(path.parts and path.parts[0] == "output", f"{label} must be under output/")
    return path.as_posix()


def _git_blob(commit_sha: str, path: str, label: str) -> bytes:
    result = _git(["show", f"{commit_sha}:{path}"], check=False)
    _require(result.returncode == 0, f"{label} missing from approved report commit")
    return result.stdout


def _require_bound_blob(commit_sha: str, path: str, declared_hash: str, label: str) -> bytes:
    _require(SHA256_RE.fullmatch(declared_hash.lower()) is not None, f"invalid sha256 for {label}")
    data = _git_blob(commit_sha, path, label)
    _require(_sha256_bytes(data) == _normalise_hash(declared_hash), f"{label} hash is not bound to approved report commit")
    return data


def validate_git_binding(authority_path: str) -> dict[str, Any]:
    authority_bytes = open(authority_path, "rb").read()
    authority = _load_json_bytes(authority_bytes, "delivery authority")

    candidate_sha = str(authority.get("assured_candidate_head_sha", ""))
    approved_commit = str(authority.get("approved_report_commit_sha", ""))
    _require_commit(candidate_sha, "assured candidate head")
    _require_commit(approved_commit, "approved report commit")

    head = _git(["rev-parse", "HEAD"]).stdout.decode("ascii").strip()
    _require_commit(head, "current checkout head")
    _require_ancestor(candidate_sha, approved_commit, "assured candidate is not an ancestor of approved report commit")
    _require_ancestor(approved_commit, head, "approved report commit is not in current checkout lineage")

    assurance = authority.get("independent_assurance")
    _require(isinstance(assurance, dict), "independent_assurance object required")
    _require(str(assurance.get("reviewed_head_sha", "")) == candidate_sha, "independent assurance is not bound to assured candidate")

    manifest_binding = authority.get("thin_kernel_manifest")
    _require(isinstance(manifest_binding, dict), "thin_kernel_manifest binding required")
    manifest_path = _repo_path(manifest_binding.get("path"), "thin kernel manifest")
    manifest_hash = str(manifest_binding.get("sha256", ""))
    manifest_bytes = _require_bound_blob(approved_commit, manifest_path, manifest_hash, "thin kernel manifest")
    manifest = _load_json_bytes(manifest_bytes, "approved thin kernel manifest")

    safety_binding = authority.get("client_surface_safety")
    _require(isinstance(safety_binding, dict), "client_surface_safety object required")
    safety_path = _repo_path(safety_binding.get("evidence_ref"), "client surface safety evidence")
    safety_hash = str(safety_binding.get("evidence_sha256", ""))
    _require_bound_blob(approved_commit, safety_path, safety_hash, "client surface safety evidence")

    manifest_artifacts = manifest.get("artifacts")
    authority_artifacts = authority.get("artifacts")
    _require(isinstance(manifest_artifacts, dict), "approved thin kernel artifacts object required")
    _require(isinstance(authority_artifacts, dict), "authority artifacts object required")

    review_state = manifest_artifacts.get("review_state")
    _require(isinstance(review_state, dict), "approved review_state binding required")
    review_state_path = _repo_path(review_state.get("path"), "review_state")
    review_state_hash = str(review_state.get("sha256", ""))
    _require_bound_blob(approved_commit, review_state_path, review_state_hash, "review_state")

    for key in REQUIRED_ARTIFACT_KEYS:
        source = manifest_artifacts.get(key)
        item = authority_artifacts.get(key)
        _require(isinstance(source, dict), f"approved thin kernel artifact missing: {key}")
        _require(isinstance(item, dict), f"authority artifact missing: {key}")
        source_path = _repo_path(source.get("path"), f"thin kernel artifact {key}")
        item_path = _repo_path(item.get("path"), f"authority artifact {key}")
        _require(item_path == source_path, f"authority artifact path differs from approved thin kernel manifest: {key}")
        source_hash = str(source.get("sha256", ""))
        item_hash = str(item.get("sha256", ""))
        _require(_normalise_hash(item_hash) == _normalise_hash(source_hash), f"authority artifact hash differs from approved thin kernel manifest: {key}")
        _require_bound_blob(approved_commit, item_path, item_hash, f"artifact {key}")

    return {
        "assured_candidate_head_sha": candidate_sha,
        "approved_report_commit_sha": approved_commit,
        "current_head_sha": head,
        "git_binding_valid": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail closed unless ETF EU guarded-delivery authority is bound to reviewed Git lineage and committed artifacts")
    parser.add_argument("--authority", required=True)
    args = parser.parse_args()
    result = validate_git_binding(args.authority)
    print(
        "ETF_EU_GUARDED_DELIVERY_GIT_BINDING_OK"
        f" | candidate={result['assured_candidate_head_sha']}"
        f" | approved_commit={result['approved_report_commit_sha']}"
        f" | current_head={result['current_head_sha']}"
    )


if __name__ == "__main__":
    main()
