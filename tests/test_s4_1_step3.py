"""Step 3 verification for Story S4.1: ignore-pattern union merging."""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".agent" / "ai_assistant.py"

AGENT_DEFAULTS = {
    ".aider.conf.yml": "model: gpt-4o\nauto_commits: false\n",
    ".aider.model.settings.yml": (
        "- name: gpt-4o\n  extra_params:\n    - temperature: 0.5\n"
    ),
    ".aider.model.metadata.json": '{\n  "gpt-4o": {"max_input_tokens": 128000}\n}\n',
    ".aiderignore": "# agent ignore\nnode_modules\n*.log\n",
}

ROOT_OVERRIDES = {
    ".aider.conf.yml": "auto_commits: true\nweak_model: gpt-4o-mini\n",
    ".aider.model.settings.yml": (
        "- name: gpt-4o\n  extra_params:\n    - temperature: 0.9\n"
    ),
    ".aider.model.metadata.json": '{\n  "gpt-4o": {"max_output_tokens": 16384}\n}\n',
    ".aiderignore": "# root ignore\ndist\nbuild/\n",
}


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
    for name, content in AGENT_DEFAULTS.items():
        (agent_dir / name).write_text(content, encoding="utf-8")
    return tmp_path


def _write_root_counterparts(workspace, names):
    for name in names:
        (workspace / name).write_text(ROOT_OVERRIDES[name], encoding="utf-8")


def test_merge_aiderignore_unions_distinct_patterns(assistant, workspace):
    agent_file = workspace / ".agent" / ".aiderignore"
    root_file = workspace / ".aiderignore"
    root_file.write_text(ROOT_OVERRIDES[".aiderignore"], encoding="utf-8")

    patterns = assistant._merge_aiderignore(agent_file, root_file)

    assert patterns == ["node_modules", "*.log", "dist", "build/"]


def test_merge_aiderignore_deduplicates(assistant, tmp_path):
    agent_file = tmp_path / "agent-ignore"
    root_file = tmp_path / "root-ignore"
    agent_file.write_text("node_modules\n*.log\n", encoding="utf-8")
    root_file.write_text("*.log\nnode_modules\n", encoding="utf-8")

    patterns = assistant._merge_aiderignore(agent_file, root_file)

    assert patterns == ["node_modules", "*.log"]


def test_merge_aiderignore_excludes_comments_and_blanks(assistant, tmp_path):
    agent_file = tmp_path / "agent-ignore"
    root_file = tmp_path / "root-ignore"
    agent_file.write_text("# comment\n\nnode_modules\n", encoding="utf-8")
    root_file.write_text("\n   \n# another\ndist\n", encoding="utf-8")

    patterns = assistant._merge_aiderignore(agent_file, root_file)

    assert patterns == ["node_modules", "dist"]


def test_merge_aiderignore_preserves_negation_patterns(assistant, tmp_path):
    agent_file = tmp_path / "agent-ignore"
    root_file = tmp_path / "root-ignore"
    agent_file.write_text("*.log\n!keep.log\n", encoding="utf-8")
    root_file.write_text("!keep.log\ndist\n", encoding="utf-8")

    patterns = assistant._merge_aiderignore(agent_file, root_file)

    assert patterns == ["*.log", "!keep.log", "dist"]


def test_merge_aiderignore_drops_trailing_whitespace(assistant, tmp_path):
    agent_file = tmp_path / "agent-ignore"
    root_file = tmp_path / "root-ignore"
    agent_file.write_text("node_modules   \n", encoding="utf-8")
    root_file.write_text("node_modules\n", encoding="utf-8")

    patterns = assistant._merge_aiderignore(agent_file, root_file)

    assert patterns == ["node_modules"]


def test_merged_ignore_intermediate_is_deterministic(assistant, workspace):
    _write_root_counterparts(workspace, [".aiderignore"])
    agent_dir = workspace / ".agent"
    agent_file = agent_dir / ".aiderignore"
    root_file = workspace / ".aiderignore"

    first = assistant._write_merged_ignore_file(
        agent_dir, agent_file, root_file, debug=False
    )
    first_bytes = first.read_bytes()
    first.unlink()

    second = assistant._write_merged_ignore_file(
        agent_dir, agent_file, root_file, debug=False
    )

    assert second == first
    assert second.read_bytes() == first_bytes


def test_merged_ignore_intermediate_holds_union(assistant, workspace):
    _write_root_counterparts(workspace, [".aiderignore"])
    agent_dir = workspace / ".agent"

    merged_path = assistant._write_merged_ignore_file(
        agent_dir,
        agent_dir / ".aiderignore",
        workspace / ".aiderignore",
        debug=False,
    )

    assert merged_path == agent_dir / ".merged" / ".aiderignore"
    assert merged_path.read_text(encoding="utf-8") == (
        "node_modules\n*.log\ndist\nbuild/\n"
    )


def test_merged_ignore_set_is_order_independent(assistant, tmp_path):
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()
    first_agent = agent_dir / "a"
    first_root = tmp_path / "b"
    second_agent = agent_dir / "c"
    second_root = tmp_path / "d"
    first_agent.write_text("alpha\nbeta\n", encoding="utf-8")
    first_root.write_text("gamma\n", encoding="utf-8")
    second_agent.write_text("gamma\nbeta\n", encoding="utf-8")
    second_root.write_text("alpha\n", encoding="utf-8")

    first = assistant._merge_aiderignore(first_agent, first_root)
    second = assistant._merge_aiderignore(second_agent, second_root)

    assert sorted(first) == sorted(second) == ["alpha", "beta", "gamma"]


def test_merged_config_args_both_ignore_copies_points_at_intermediate(
    assistant, workspace
):
    _write_root_counterparts(workspace, [".aiderignore"])
    agent_dir = workspace / ".agent"

    args = assistant._merged_config_args(
        agent_dir, assistant._root_config_counterparts(workspace), debug=False
    )

    ignore_index = args.index("--aiderignore")
    assert args[ignore_index + 1] == str(agent_dir / ".merged" / ".aiderignore")


def test_merged_config_args_agent_ignore_only_passes_through(assistant, workspace):
    _write_root_counterparts(workspace, [".aider.conf.yml"])
    agent_dir = workspace / ".agent"

    args = assistant._merged_config_args(
        agent_dir, assistant._root_config_counterparts(workspace), debug=False
    )

    ignore_index = args.index("--aiderignore")
    assert args[ignore_index + 1] == str(agent_dir / ".aiderignore")


def test_merged_config_args_root_ignore_only_points_at_root_file(assistant, workspace):
    agent_dir = workspace / ".agent"
    (agent_dir / ".aiderignore").unlink()
    _write_root_counterparts(workspace, [".aiderignore"])

    args = assistant._merged_config_args(
        agent_dir, assistant._root_config_counterparts(workspace), debug=False
    )

    ignore_index = args.index("--aiderignore")
    assert args[ignore_index + 1] == str(workspace / ".aiderignore")


def test_merged_config_args_no_counterparts_matches_passthrough(assistant, workspace):
    agent_dir = workspace / ".agent"

    assert assistant._merged_config_args(agent_dir, {}, debug=False) == (
        assistant._aider_config_args(agent_dir)
    )


def test_write_merged_ignore_file_falls_back_on_write_failure(assistant, workspace):
    _write_root_counterparts(workspace, [".aiderignore"])
    agent_dir = workspace / ".agent"
    (agent_dir / ".merged").write_text("not a directory\n", encoding="utf-8")

    merged_path = assistant._write_merged_ignore_file(
        agent_dir,
        agent_dir / ".aiderignore",
        workspace / ".aiderignore",
        debug=False,
    )

    assert merged_path is None


def test_write_merged_ignore_file_falls_back_on_read_failure(assistant, tmp_path):
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()
    agent_file = agent_dir / ".aiderignore"
    root_file = tmp_path / ".aiderignore"
    agent_file.write_text("node_modules\n", encoding="utf-8")
    root_file.write_text("dist\n", encoding="utf-8")
    # A directory in place of the agent file makes its read fail.
    agent_file.unlink()
    agent_file.mkdir()

    merged_path = assistant._write_merged_ignore_file(
        agent_dir, agent_file, root_file, debug=False
    )

    assert merged_path is None
