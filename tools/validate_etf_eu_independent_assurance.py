from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

MARKER = "ETF_EU_INDEPENDENT_ASSURANCE_V1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
EXPECTED_REPOSITORY_FULL_NAME = "market-predictions/weekly-etf-eu"
TRUSTED_INDEPENDENT_REVIEWER_LOGINS = {"chatgpt-codex-connector[bot]"}
_PULL_API_RE = re.compile(
    r"^https://api\.github\.com/repos/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pulls/(?P<pr>\d+)$"
)
_REVIEW_API_RE = re.compile(
    r"^https://api\.github\.com/repos/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pulls/(?P<pr>\d+)/reviews/(?P<review>\d+)$"
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _normalise_hash(value: str) -> str:
    value = value.lower()
    return value if value.startswith("sha256:") else "sha256:" + value


def _pull_identity(pull_url: str) -> tuple[str, int, str]:
    match = _PULL_API_RE.fullmatch(pull_url.rstrip("/"))
    _require(match is not None, "independent assurance pull_request_url must be a GitHub API pull URL")
    repository = f"{match.group('owner')}/{match.group('repo')}"
    _require(
        repository == EXPECTED_REPOSITORY_FULL_NAME,
        "independent assurance review is not bound to market-predictions/weekly-etf-eu",
    )
    return repository, int(match.group("pr")), pull_url.rstrip("/")


def _review_api_url(review: dict[str, Any]) -> tuple[str, str, int, str]:
    review_id = str(review.get("id") or "")
    pull_url = str(review.get("pull_request_url") or "")
    _require(review_id.isdigit(), "independent assurance review id missing")
    repository, pr_number, canonical_pull_url = _pull_identity(pull_url)
    return canonical_pull_url + f"/reviews/{review_id}", repository, pr_number, canonical_pull_url


def _body_tuple(body: str) -> dict[str, str]:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    _require(MARKER in lines, "independent assurance marker missing")
    keys = (
        "verdict",
        "reviewer_role",
        "implementation_role_separate",
        "candidate_sha",
        "expected_base_branch",
        "expected_base_sha",
    )
    values: dict[str, str] = {}
    for key in keys:
        matches = [line.split("=", 1)[1].strip() for line in lines if line.startswith(key + "=")]
        _require(len(matches) == 1, f"independent assurance body must contain exactly one {key}")
        values[key] = matches[0]
    return values


def _binding_payload(review: dict[str, Any]) -> dict[str, Any]:
    user = review.get("user")
    _require(isinstance(user, dict), "independent assurance reviewer identity missing")
    login = str(user.get("login") or "").strip()
    _require(bool(login), "independent assurance reviewer login missing")
    _require(
        login in TRUSTED_INDEPENDENT_REVIEWER_LOGINS,
        "independent assurance reviewer is not a trusted independent reviewer identity",
    )
    return {
        "id": int(review.get("id")),
        "state": str(review.get("state") or ""),
        "body": str(review.get("body") or ""),
        "commit_id": str(review.get("commit_id") or ""),
        "html_url": str(review.get("html_url") or ""),
        "pull_request_url": str(review.get("pull_request_url") or ""),
        "reviewer_login": login,
        "submitted_at": str(review.get("submitted_at") or ""),
    }


def binding_sha256(review: dict[str, Any]) -> str:
    canonical = json.dumps(
        _binding_payload(review), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _validate_parent_pull(
    pull: dict[str, Any],
    *,
    repository_full_name: str,
    pr_number: int,
    pull_api_url: str,
    candidate_sha: str,
    expected_base_branch: str,
    expected_base_sha: str,
) -> None:
    _require(int(pull.get("number") or 0) == pr_number, "independent assurance parent PR number mismatch")
    _require(str(pull.get("url") or "").rstrip("/") == pull_api_url, "independent assurance parent PR URL mismatch")
    head = pull.get("head")
    base = pull.get("base")
    _require(isinstance(head, dict) and isinstance(base, dict), "independent assurance parent PR head/base missing")
    head_repo = head.get("repo")
    base_repo = base.get("repo")
    _require(isinstance(head_repo, dict) and isinstance(base_repo, dict), "independent assurance parent PR repository identity missing")
    _require(
        str(head_repo.get("full_name") or "") == repository_full_name
        and str(base_repo.get("full_name") or "") == repository_full_name,
        "independent assurance parent PR repository mismatch",
    )
    _require(str(head.get("sha") or "").lower() == candidate_sha.lower(), "independent assurance parent PR head mismatch")
    _require(str(base.get("ref") or "") == expected_base_branch, "independent assurance parent PR base branch mismatch")
    _require(str(base.get("sha") or "").lower() == expected_base_sha.lower(), "independent assurance parent PR base sha mismatch")


def validate_review(
    review: dict[str, Any],
    *,
    candidate_sha: str,
    expected_base_branch: str,
    expected_base_sha: str,
    expected_pr_number: int | None = None,
    evidence_api_url: str | None = None,
    evidence_binding_sha256: str | None = None,
) -> dict[str, Any]:
    candidate_sha = candidate_sha.lower()
    expected_base_sha = expected_base_sha.lower()
    _require(SHA_RE.fullmatch(candidate_sha) is not None, "invalid assurance candidate sha")
    _require(bool(expected_base_branch.strip()), "assurance expected base branch required")
    _require(SHA_RE.fullmatch(expected_base_sha) is not None, "invalid assurance expected base sha")
    _require(
        str(review.get("state") or "").upper() in {"COMMENTED", "APPROVED"},
        "independent assurance review state is not acceptable",
    )
    _require(
        str(review.get("commit_id") or "").lower() == candidate_sha,
        "independent assurance review commit/candidate mismatch",
    )
    values = _body_tuple(str(review.get("body") or ""))
    _require(values["verdict"] == "PASS", "independent assurance verdict must be PASS")
    _require(values["reviewer_role"] == "governance_release_assurance", "independent assurance reviewer role mismatch")
    _require(values["implementation_role_separate"].lower() == "true", "assurance independence not evidenced")
    _require(values["candidate_sha"].lower() == candidate_sha, "independent assurance body candidate mismatch")
    _require(values["expected_base_branch"] == expected_base_branch, "independent assurance base branch mismatch")
    _require(values["expected_base_sha"].lower() == expected_base_sha, "independent assurance base sha mismatch")

    api_url, repository, pr_number, _pull_url = _review_api_url(review)
    if expected_pr_number is not None:
        _require(pr_number == expected_pr_number, "independent assurance PR number mismatch")
    if evidence_api_url is not None:
        _require(api_url == evidence_api_url, "independent assurance evidence API reference mismatch")
    digest = binding_sha256(review)
    if evidence_binding_sha256 is not None:
        _require(SHA256_RE.fullmatch(evidence_binding_sha256.lower()) is not None, "invalid independent assurance evidence binding sha256")
        _require(_normalise_hash(evidence_binding_sha256) == digest, "independent assurance evidence binding hash mismatch")
    binding = _binding_payload(review)
    return {
        "verdict": "PASS",
        "reviewer_role": "governance_release_assurance",
        "implementation_role_separate": True,
        "repository_full_name": repository,
        "pr_number": pr_number,
        "reviewed_head_sha": candidate_sha,
        "expected_base_branch": expected_base_branch,
        "expected_base_sha": expected_base_sha,
        "evidence_ref": api_url,
        "evidence_html_url": binding["html_url"],
        "evidence_binding_sha256": digest,
        "review_id": binding["id"],
        "reviewer_login": binding["reviewer_login"],
        "submitted_at": binding["submitted_at"],
    }


def validate_review_file(path: Path, **kwargs: Any) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(payload, dict), "independent assurance evidence must be a JSON object")
    return validate_review(payload, **kwargs)


def _fetch_github_json(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    _require(parsed.scheme == "https" and parsed.netloc == "api.github.com", "independent assurance GitHub URL must use api.github.com")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise AssertionError("independent assurance evidence could not be resolved from GitHub") from exc
    _require(isinstance(payload, dict), "resolved independent assurance GitHub evidence must be an object")
    return payload


def resolve_review(
    *,
    evidence_api_url: str,
    candidate_sha: str,
    expected_base_branch: str,
    expected_base_sha: str,
    expected_pr_number: int | None = None,
    evidence_binding_sha256: str | None = None,
    evidence_path: Path | None = None,
) -> dict[str, Any]:
    match = _REVIEW_API_RE.fullmatch(evidence_api_url)
    _require(match is not None, "independent assurance evidence is not a GitHub PR review")
    repository = f"{match.group('owner')}/{match.group('repo')}"
    _require(repository == EXPECTED_REPOSITORY_FULL_NAME, "independent assurance evidence repository mismatch")
    pr_number = int(match.group("pr"))
    if expected_pr_number is not None:
        _require(pr_number == expected_pr_number, "independent assurance evidence PR mismatch")
    pull_api_url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}"

    if evidence_path is not None:
        return validate_review_file(
            evidence_path,
            candidate_sha=candidate_sha,
            expected_base_branch=expected_base_branch,
            expected_base_sha=expected_base_sha,
            expected_pr_number=pr_number,
            evidence_api_url=evidence_api_url,
            evidence_binding_sha256=evidence_binding_sha256,
        )

    review = _fetch_github_json(evidence_api_url)
    resolved = validate_review(
        review,
        candidate_sha=candidate_sha,
        expected_base_branch=expected_base_branch,
        expected_base_sha=expected_base_sha,
        expected_pr_number=pr_number,
        evidence_api_url=evidence_api_url,
        evidence_binding_sha256=evidence_binding_sha256,
    )
    parent_pull = _fetch_github_json(pull_api_url)
    _validate_parent_pull(
        parent_pull,
        repository_full_name=repository,
        pr_number=pr_number,
        pull_api_url=pull_api_url,
        candidate_sha=candidate_sha,
        expected_base_branch=expected_base_branch,
        expected_base_sha=expected_base_sha,
    )
    return resolved
