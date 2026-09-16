"""Step 1 verification for Story S4.1: config counterpart discovery."""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".agent" / "ai_assistant.py"

CONFIG_FILE_NAMES = (
    ".aider.conf.yml",
    ".aider.model.settings.yml",
    ".aiderignore",
    ".aider.model.metadata.json",
)


def _load_assistant_module():
    spec = importlib.util.spec_from_file_location("ai_assistant", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def assistant():
    return _load_assistant_module()


@pytest.fixture()
def workspace(tmp_path):
    """A project root with an .agent directory holding all default copies."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()
    for name in CONFIG_FILE_NAMES:
        (agent_dir / name).write_text("default\n", encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("name", CONFIG_FILE_NAMES)
def test_detects_each_counterpart(assistant, workspace, name):
    (workspace / name).write_text("root\n", encoding="utf-8")

    detected = assistant._root_config_counterparts(workspace)

    assert detected == {name: workspace / name}


def test_detects_mixed_counterparts_independently(assistant, workspace):
    present = (".aider.conf.yml", ".aiderignore")
    for name in present:
        (workspace / name).write_text("root\n", encoding="utf-8")

    detected = assistant._root_config_counterparts(workspace)

    assert sorted(detected) == list(present)
    assert all(detected[name] == workspace / name for name in present)


def test_no_counterparts_returns_empty(assistant, workspace):
    assert assistant._root_config_counterparts(workspace) == {}


def test_mergeable_files_cover_all_four_configs(assistant):
    assert sorted(assistant.MERGEABLE_CONFIG_FILES) == sorted(CONFIG_FILE_NAMES)


def test_no_counterparts_keeps_flag_assembly_unchanged(assistant, workspace):
    agent_dir = workspace / ".agent"

    args = assistant._aider_config_args(agent_dir)

    assert args == [
        "--config",
        str(agent_dir / ".aider.conf.yml"),
        "--model-settings-file",
        str(agent_dir / ".aider.model.settings.yml"),
        "--aiderignore",
        str(agent_dir / ".aiderignore"),
        "--model-metadata-file",
        str(agent_dir / ".aider.model.metadata.json"),
    ]
