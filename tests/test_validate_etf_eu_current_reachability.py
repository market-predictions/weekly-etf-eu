from __future__ import annotations

from pathlib import Path

import tools.validate_etf_eu_current_reachability as reachability


def _configure_tmp_roots(tmp_path: Path, monkeypatch) -> tuple[Path, Path, Path]:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    current_builder = tmp_path / "tools" / "build_etf_eu_thin_kernel_package.py"
    current_builder.parent.mkdir(parents=True)
    current_builder.write_text("# current builder\n", encoding="utf-8")
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir(parents=True)
    for name in reachability.REQUIRED_TOP_LEVEL_RUNTIME_FILES:
        (runtime_dir / name).write_text("# canonical runtime helper\n", encoding="utf-8")
    current_runtime = runtime_dir / "current"
    current_runtime.mkdir(parents=True)
    (current_runtime / "kernel.py").write_text("# current runtime\n", encoding="utf-8")
    controlled = workflow_dir / "send-weekly-etf-eu-controlled-transport.yml"

    monkeypatch.setattr(reachability, "WORKFLOW_DIR", workflow_dir)
    monkeypatch.setattr(reachability, "CURRENT_BUILDER", current_builder)
    monkeypatch.setattr(reachability, "RUNTIME_DIR", runtime_dir)
    monkeypatch.setattr(reachability, "CURRENT_RUNTIME_DIR", current_runtime)
    monkeypatch.setattr(reachability, "CONTROLLED_TRANSPORT_WORKFLOW", controlled)
    return workflow_dir, controlled, runtime_dir


def _guarded_transport_text() -> str:
    return "\n".join(reachability.CONTROLLED_TRANSPORT_REQUIRED_MARKERS) + "\n"


def test_governed_transport_is_only_allowed_direct_main_writer(tmp_path: Path, monkeypatch) -> None:
    _, controlled, _ = _configure_tmp_roots(tmp_path, monkeypatch)
    controlled.write_text(_guarded_transport_text(), encoding="utf-8")

    result = reachability.validate()

    assert result["valid"] is True
    assert result["verdict"] == "PASS"
    assert result["blockers"] == []
    assert result["controlled_transport_main_write_exception"]["workflow"] == str(controlled)


def test_non_transport_direct_main_write_fails_closed(tmp_path: Path, monkeypatch) -> None:
    workflow_dir, controlled, _ = _configure_tmp_roots(tmp_path, monkeypatch)
    controlled.write_text(_guarded_transport_text(), encoding="utf-8")
    (workflow_dir / "diagnostic.yml").write_text("run: git push origin HEAD:main\n", encoding="utf-8")

    result = reachability.validate()

    assert result["valid"] is False
    assert {
        "type": "direct_main_write_reachable",
        "path": str(workflow_dir / "diagnostic.yml"),
        "token": "git push origin HEAD:main",
    } in result["blockers"]


def test_controlled_transport_missing_any_required_guard_fails_closed(tmp_path: Path, monkeypatch) -> None:
    _, controlled, _ = _configure_tmp_roots(tmp_path, monkeypatch)
    missing = "confirm_guarded_send_second"
    controlled.write_text(
        "\n".join(marker for marker in reachability.CONTROLLED_TRANSPORT_REQUIRED_MARKERS if marker != missing) + "\n",
        encoding="utf-8",
    )

    result = reachability.validate()

    assert result["valid"] is False
    assert {
        "type": "controlled_transport_main_write_guard_missing",
        "path": str(controlled),
        "token": missing,
    } in result["blockers"]


def test_unexpected_top_level_runtime_executor_fails_closed(tmp_path: Path, monkeypatch) -> None:
    _, controlled, runtime_dir = _configure_tmp_roots(tmp_path, monkeypatch)
    controlled.write_text(_guarded_transport_text(), encoding="utf-8")
    legacy = runtime_dir / "render_etf_eu_report.py"
    legacy.write_text("# legacy executor\n", encoding="utf-8")

    result = reachability.validate()

    assert result["valid"] is False
    assert {
        "type": "unexpected_top_level_runtime_executor",
        "path": str(legacy),
        "token": legacy.name,
    } in result["blockers"]


def test_unexpected_runtime_subdirectory_fails_closed(tmp_path: Path, monkeypatch) -> None:
    _, controlled, runtime_dir = _configure_tmp_roots(tmp_path, monkeypatch)
    controlled.write_text(_guarded_transport_text(), encoding="utf-8")
    legacy_dir = runtime_dir / "shadow"
    legacy_dir.mkdir()

    result = reachability.validate()

    assert result["valid"] is False
    assert {
        "type": "unexpected_top_level_runtime_directory",
        "path": str(legacy_dir),
        "token": legacy_dir.name,
    } in result["blockers"]
