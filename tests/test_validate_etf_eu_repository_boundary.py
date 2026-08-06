from pathlib import Path

from tools.validate_etf_eu_repository_boundary import validate


def test_clean_etf_eu_repository_passes(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "weekly-etf-eu.yml").write_text(
        "name: Weekly ETF EU\non: workflow_dispatch\njobs: {}\n",
        encoding="utf-8",
    )
    result = validate(tmp_path)
    assert result["verdict"] == "PASS"


def test_fx_workflow_is_blocked(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "generate_predictions.yml").write_text(
        "name: FX\nsteps:\n  - run: python prediction.py\n",
        encoding="utf-8",
    )
    result = validate(tmp_path)
    assert result["verdict"] == "FAIL"
    assert any(item["type"] == "fx_token_in_active_workflow" for item in result["blockers"])


def test_fx_root_assets_are_blocked(tmp_path: Path) -> None:
    (tmp_path / "prediction.py").write_text("print('fx')\n", encoding="utf-8")
    (tmp_path / "daily_outputs").mkdir()
    result = validate(tmp_path)
    assert result["verdict"] == "FAIL"
    paths = {item["path"] for item in result["blockers"]}
    assert "prediction.py" in paths
    assert "daily_outputs" in paths
