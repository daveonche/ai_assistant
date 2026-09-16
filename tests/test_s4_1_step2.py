"""Step 2 verification for Story S4.1: value-based config merging."""

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".agent" / "ai_assistant.py"

AGENT_DEFAULTS = {
    ".aider.conf.yml": (
        "model: gpt-4o\n"
        "auto_commits: false\n"
        "edit_format: diff\n"
    ),
    ".aider.model.settings.yml": (
        "- name: gpt-4o\n"
        "  extra_params:\n"
        "    - temperature: 0.5\n"
        "- name: legacy-model\n"
        "  extra_params:\n"
        "    - temperature: 0.2\n"
    ),
    ".aider.model.metadata.json": (
        '{\n  "gpt-4o": {"max_input_tokens": 128000}\n}\n'
    ),
    ".aiderignore": "node_modules\n",
}

ROOT_OVERRIDES = {
    ".aider.conf.yml": (
        "# project override\n"
        "auto_commits: true\n"
        "weak_model: gpt-4o-mini\n"
    ),
    ".aider.model.settings.yml": (
        "- name: gpt-4o\n"
        "  extra_params:\n"
        "    - temperature: 0.9\n"
        "- name: root-only-model\n"
        "  extra_params:\n"
        "    - temperature: 0.1\n"
    ),
    ".aider.model.metadata.json": (
        '{\n  "gpt-4o": {"max_output_tokens": 16384},\n'
        '  "root-only-model": {"notes": "added"}\n}\n'
    ),
    ".aiderignore": "dist\n",
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


def test_deep_merge_combines_nested_levels(assistant):
    base = {"a": {"b": {"c": 1, "d": 2}}, "keep": "me"}
    override = {"a": {"b": {"c": 9}}}

    merged = assistant._deep_merge(base, override)

    assert merged == {"a": {"b": {"c": 9, "d": 2}}, "keep": "me"}


def test_deep_merge_root_wins_conflicts(assistant):
    assert assistant._deep_merge({"k": "agent"}, {"k": "root"}) == {"k": "root"}


def test_deep_merge_retains_unset_defaults(assistant):
    merged = assistant._deep_merge({"only_agent": 1}, {"only_root": 2})

    assert merged == {"only_agent": 1, "only_root": 2}


def test_deep_merge_does_not_mutate_inputs(assistant):
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}

    assistant._deep_merge(base, override)

    assert base == {"a": {"b": 1}}
    assert override == {"a": {"c": 2}}


def test_model_settings_merge_by_name(assistant):
    base = [
        {"name": "gpt-4o", "extra_params": [{"temperature": 0.5}]},
        {"name": "legacy-model", "extra_params": [{"temperature": 0.2}]},
    ]
    override = [
        {"name": "gpt-4o", "extra_params": [{"temperature": 0.9}]},
        {"name": "root-only-model", "extra_params": [{"temperature": 0.1}]},
    ]

    merged = assistant._merge_model_settings(base, override)

    assert merged == [
        {"name": "gpt-4o", "extra_params": [{"temperature": 0.9}]},
        {"name": "legacy-model", "extra_params": [{"temperature": 0.2}]},
        {"name": "root-only-model", "extra_params": [{"temperature": 0.1}]},
    ]


def test_model_settings_non_list_falls_back_to_deep_merge(assistant):
    assert assistant._merge_model_settings({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_yaml_load_block_mapping(assistant):
    doc = assistant._yaml_load(AGENT_DEFAULTS[".aider.conf.yml"])

    assert doc == {
        "model": "gpt-4o",
        "auto_commits": False,
        "edit_format": "diff",
    }


def test_yaml_load_sequence_of_mappings(assistant):
    doc = assistant._yaml_load(AGENT_DEFAULTS[".aider.model.settings.yml"])

    assert doc == [
        {"name": "gpt-4o", "extra_params": [{"temperature": 0.5}]},
        {"name": "legacy-model", "extra_params": [{"temperature": 0.2}]},
    ]


@pytest.mark.parametrize(
    "text",
    [
        "flow: {a: 1}\n",
        "anchor: &base 1\nuse: *base\n",
        "block: |\n  line one\n",
        "key:\n\t- tabbed\n",
        "---\nkey: 1\n",
    ],
)
def test_yaml_load_rejects_unsupported_syntax(assistant, text):
    with pytest.raises(ValueError):
        assistant._yaml_load(text)


def test_yaml_round_trip_preserves_values(assistant):
    for name in (".aider.conf.yml", ".aider.model.settings.yml"):
        doc = assistant._yaml_load(AGENT_DEFAULTS[name])
        dumped = assistant._yaml_dump(doc)

        assert assistant._yaml_load(dumped) == doc


def test_merged_intermediate_is_deterministic(assistant, workspace):
    _write_root_counterparts(workspace, [".aider.conf.yml"])
    agent_dir = workspace / ".agent"
    agent_file = agent_dir / ".aider.conf.yml"
    root_file = workspace / ".aider.conf.yml"

    first = assistant._write_merged_value_file(
        agent_dir, ".aider.conf.yml", agent_file, root_file, debug=False
    )
    first_bytes = first.read_bytes()
    first.unlink()

    second = assistant._write_merged_value_file(
        agent_dir, ".aider.conf.yml", agent_file, root_file, debug=False
    )

    assert second == first
    assert second.read_bytes() == first_bytes


def test_json_metadata_merge_root_wins_and_retains(assistant, tmp_path):
    agent_file = tmp_path / "agent.json"
    root_file = tmp_path / "root.json"
    agent_file.write_text(
        '{"gpt-4o": {"max_input_tokens": 128000}}\n', encoding="utf-8"
    )
    root_file.write_text(
        '{"gpt-4o": {"max_output_tokens": 16384}, "other": {}}\n', encoding="utf-8"
    )

    merged = assistant._merge_json_documents(agent_file, root_file)

    assert merged == {
        "gpt-4o": {"max_input_tokens": 128000, "max_output_tokens": 16384},
        "other": {},
    }


def test_write_merged_value_file_creates_intermediate(assistant, workspace):
    _write_root_counterparts(workspace, [".aider.conf.yml"])
    agent_dir = workspace / ".agent"

    merged_path = assistant._write_merged_value_file(
        agent_dir,
        ".aider.conf.yml",
        agent_dir / ".aider.conf.yml",
        workspace / ".aider.conf.yml",
        debug=False,
    )

    assert merged_path == agent_dir / ".merged" / ".aider.conf.yml"
    doc = assistant._yaml_load(merged_path.read_text(encoding="utf-8"))
    assert doc == {
        "model": "gpt-4o",
        "auto_commits": True,
        "edit_format": "diff",
        "weak_model": "gpt-4o-mini",
    }


def test_write_merged_model_settings_merges_by_name(assistant, workspace):
    _write_root_counterparts(workspace, [".aider.model.settings.yml"])
    agent_dir = workspace / ".agent"

    merged_path = assistant._write_merged_value_file(
        agent_dir,
        ".aider.model.settings.yml",
        agent_dir / ".aider.model.settings.yml",
        workspace / ".aider.model.settings.yml",
        debug=False,
    )

    doc = assistant._yaml_load(merged_path.read_text(encoding="utf-8"))
    assert doc == [
        {"name": "gpt-4o", "extra_params": [{"temperature": 0.9}]},
        {"name": "legacy-model", "extra_params": [{"temperature": 0.2}]},
        {"name": "root-only-model", "extra_params": [{"temperature": 0.1}]},
    ]


def test_write_merged_metadata_creates_intermediate(assistant, workspace):
    _write_root_counterparts(workspace, [".aider.model.metadata.json"])
    agent_dir = workspace / ".agent"

    merged_path = assistant._write_merged_value_file(
        agent_dir,
        ".aider.model.metadata.json",
        agent_dir / ".aider.model.metadata.json",
        workspace / ".aider.model.metadata.json",
        debug=False,
    )

    assert merged_path == agent_dir / ".merged" / ".aider.model.metadata.json"
    assert json.loads(merged_path.read_text(encoding="utf-8")) == {
        "gpt-4o": {"max_input_tokens": 128000, "max_output_tokens": 16384},
        "root-only-model": {"notes": "added"},
    }


def test_write_merged_value_file_falls_back_on_unparseable(assistant, workspace):
    (workspace / ".aider.conf.yml").write_text("flow: {a: 1}\n", encoding="utf-8")
    agent_dir = workspace / ".agent"

    merged_path = assistant._write_merged_value_file(
        agent_dir,
        ".aider.conf.yml",
        agent_dir / ".aider.conf.yml",
        workspace / ".aider.conf.yml",
        debug=False,
    )

    assert merged_path is None


def test_merged_config_args_no_counterparts_matches_passthrough(assistant, workspace):
    agent_dir = workspace / ".agent"

    assert assistant._merged_config_args(agent_dir, {}, debug=False) == (
        assistant._aider_config_args(agent_dir)
    )


def test_merged_config_args_both_present_points_at_intermediate(assistant, workspace):
    _write_root_counterparts(workspace, list(assistant.VALUE_CONFIG_FLAGS))
    agent_dir = workspace / ".agent"

    args = assistant._merged_config_args(
        agent_dir, assistant._root_config_counterparts(workspace), debug=False
    )

    for name, flag in assistant.VALUE_CONFIG_FLAGS.items():
        index = args.index(flag)
        assert args[index + 1] == str(agent_dir / ".merged" / name)
    # The .aiderignore union merge lands with the next step; with both
    # copies present the agent copy is still passed through.
    ignore_index = args.index("--aiderignore")
    assert args[ignore_index + 1] == str(agent_dir / ".aiderignore")


def test_merged_config_args_root_only_points_at_root_file(assistant, workspace):
    agent_dir = workspace / ".agent"
    (agent_dir / ".aider.conf.yml").unlink()
    _write_root_counterparts(workspace, [".aider.conf.yml"])

    args = assistant._merged_config_args(
        agent_dir, assistant._root_config_counterparts(workspace), debug=False
    )

    index = args.index("--config")
    assert args[index + 1] == str(workspace / ".aider.conf.yml")


def test_merged_config_args_mixed_counterparts(assistant, workspace):
    agent_dir = workspace / ".agent"
    _write_root_counterparts(
        workspace, [".aider.conf.yml", ".aider.model.metadata.json"]
    )

    args = assistant._merged_config_args(
        agent_dir, assistant._root_config_counterparts(workspace), debug=False
    )

    config_index = args.index("--config")
    assert args[config_index + 1] == str(agent_dir / ".merged" / ".aider.conf.yml")
    settings_index = args.index("--model-settings-file")
    assert args[settings_index + 1] == str(agent_dir / ".aider.model.settings.yml")
    metadata_index = args.index("--model-metadata-file")
    assert args[metadata_index + 1] == str(
        agent_dir / ".merged" / ".aider.model.metadata.json"
    )
    ignore_index = args.index("--aiderignore")
    assert args[ignore_index + 1] == str(agent_dir / ".aiderignore")


def test_merged_config_args_unmergeable_falls_back_to_agent_copy(assistant, workspace):
    agent_dir = workspace / ".agent"
    (workspace / ".aider.conf.yml").write_text("flow: {a: 1}\n", encoding="utf-8")

    args = assistant._merged_config_args(
        agent_dir, assistant._root_config_counterparts(workspace), debug=False
    )

    config_index = args.index("--config")
    assert args[config_index + 1] == str(agent_dir / ".aider.conf.yml")


def test_remove_merged_intermediates_removes_directory(assistant, workspace):
    agent_dir = workspace / ".agent"
    merged_dir = agent_dir / ".merged"
    merged_dir.mkdir()
    (merged_dir / ".aider.conf.yml").write_text("key: 1\n", encoding="utf-8")

    assistant._remove_merged_intermediates(agent_dir)

    assert not merged_dir.exists()


def test_remove_merged_intermediates_tolerates_missing_directory(assistant, workspace):
    assistant._remove_merged_intermediates(workspace / ".agent")
