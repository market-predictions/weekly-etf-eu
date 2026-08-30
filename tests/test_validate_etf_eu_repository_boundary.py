from pathlib import Path

from tools.validate_etf_eu_repository_boundary import validate


def test_clean_repository_passes(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "weekly-etf-eu.yml").write_text(
        "name: Weekly ETF EU\non: workflow_dispatch\njobs: {}\n",
        encoding="utf-8",
    )
    result = validate(tmp_path)
    assert result["verdict"] == "PASS"
    assert result["product"] == "weekly_etf_eu"


def test_fx_runner_is_blocked(tmp_path: Path) -> None:
    (tmp_path / "prediction.py").write_text("print('fx')\n", encoding="utf-8")
    result = validate(tmp_path)
    assert result["verdict"] == "FAIL"
    assert any(item["path"] == "prediction.py" for item in result["blockers"])


def test_fx_workflow_token_is_blocked(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "fx.yml").write_text("steps:\n  - run: python prediction.py\n", encoding="utf-8")
    result = validate(tmp_path)
    assert result["verdict"] == "FAIL"
    assert any(item["type"] == "fx_token_in_active_workflow" for item in result["blockers"])


def test_us_donor_pricing_runtime_is_blocked_in_active_workflow(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "legacy-us-pricing.yml").write_text(
        "steps:\n  - run: python -m pricing.run_pricing_pass\n",
        encoding="utf-8",
    )
    result = validate(tmp_path)
    assert result["verdict"] == "FAIL"
    assert any(
        item["type"] == "us_donor_token_in_active_workflow"
        and item["token"] == "pricing.run_pricing_pass"
        for item in result["blockers"]
    )


def test_disabled_workflow_graveyard_is_blocked(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "legacy-us-pricing.yml.disabled").write_text(
        "steps:\n  - run: python -m pricing.run_pricing_pass\n",
        encoding="utf-8",
    )
    result = validate(tmp_path)
    assert result["verdict"] == "FAIL"
    assert result["disabled_workflow_graveyard_count"] == 1
    assert any(item["type"] == "retired_disabled_workflow_in_active_namespace" for item in result["blockers"])
    assert result["retired_workflow_provenance"] == "git_history_by_default_forensic_exceptions_under_archive_workflows"


def test_legacy_us_report_renderer_is_blocked_in_active_workflow(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "legacy-render.yml").write_text(
        "steps:\n  - run: python send_report.py\n",
        encoding="utf-8",
    )
    result = validate(tmp_path)
    assert result["verdict"] == "FAIL"
    assert any(
        item["type"] == "us_donor_token_in_active_workflow"
        and item["token"] == "send_report.py"
        for item in result["blockers"]
    )
