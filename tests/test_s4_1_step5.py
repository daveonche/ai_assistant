"""Story S4.1 Step 5 checks: verification coverage for the merge behavior.

Each check launches `.agent/ai_assistant.py` in a sandbox project with a
stub `docker` on PATH and asserts on the `docker run` arguments the
launcher produces — the observable launch behavior. The launcher removes
the merged intermediates when the session ends, so the stub snapshots the
content of every config file the command points at while the session is
still running; that snapshot is exactly what the assistant would read.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_SOURCE_DIR = REPO_ROOT / ".agent"

# Flag the launcher passes for each mergeable config file (mirrors
# VALUE_CONFIG_FLAGS in ai_assistant.py plus the separately handled
# .aiderignore).
FLAG_BY_NAME = {
    ".aider.conf.yml": "--config",
    ".aider.model.settings.yml": "--model-settings-file",
    ".aiderignore": "--aiderignore",
    ".aider.model.metadata.json": "--model-metadata-file",
}

# Assistant-default fixtures, written into the sandbox .agent directory.
AGENT_CONF = """\
model: gpt-4o
map:
  refresh: true
"""

AGENT_MODEL_SETTINGS = """\
- name: provider/agent-a
  extra_params:
    temperature: 0.1
- name: provider/agent-b
  extra_params:
    max_tokens: 100
"""

AGENT_IGNORE = """\
# assistant defaults
node_modules/
*.log
dist/
"""

AGENT_METADATA = """\
{
  "provider/agent-a": {
    "max_input_tokens": 1000,
    "notes": "agent default"
  },
  "provider/agent-b": {
    "max_input_tokens": 2000
  }
}
"""

# Project-root counterpart fixtures.
ROOT_CONF = """\
model: root-override
edit-format: diff
"""

ROOT_MODEL_SETTINGS = """\
- name: provider/agent-a
  extra_params:
    temperature: 0.9
- name: provider/root-c
  extra_params:
    max_tokens: 50
"""

ROOT_IGNORE = """\
# project ignores
*.log

build/
"""

ROOT_METADATA = """\
{
  "provider/agent-a": {
    "max_input_tokens": 2000
  }
}
"""

STUB_DOCKER = """\
#!/usr/bin/env python3
# Stub docker CLI: records every invocation as a JSON line and, for
# `docker run`, snapshots the content of each config file the launcher
# pointed the assistant at. Always exits 0 so the launcher takes the
# image-cache-hit path and never builds.
import json
import os
import sys
from pathlib import Path

CONFIG_FLAGS = (
    "--config",
    "--model-settings-file",
    "--aiderignore",
    "--model-metadata-file",
)


def main() -> int:
    args = sys.argv[1:]
    entry = {"args": args, "files": {}}
    if args[:1] == ["run"]:
        for index, token in enumerate(args):
            if token in CONFIG_FLAGS and index + 1 < len(args):
                try:
                    entry["files"][token] = Path(args[index + 1]).read_text(
                        encoding="utf-8"
                    )
                except OSError:
                    entry["files"][token] = None
    log_path = Path(os.environ["STUB_LOG_PATH"])
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""


def _launcher_module():
    """Load .agent/ai_assistant.py as a module (stdlib-only, import-safe)."""
    spec = importlib.util.spec_from_file_location(
        "ai_assistant_under_test", AGENT_SOURCE_DIR / "ai_assistant.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_yaml_load = _launcher_module()._yaml_load


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_sandbox(tmp_path: Path) -> tuple[Path, Path]:
    """Create a project root with an installed .agent and a stub docker."""
    sandbox = tmp_path / "project"
    agent_dir = sandbox / ".agent"
    agent_dir.mkdir(parents=True)
    for name in ("ai_assistant.py", "Dockerfile.aider"):
        shutil.copy(AGENT_SOURCE_DIR / name, agent_dir / name)
    _write(agent_dir / ".aider.conf.yml", AGENT_CONF)
    _write(agent_dir / ".aider.model.settings.yml", AGENT_MODEL_SETTINGS)
    _write(agent_dir / ".aiderignore", AGENT_IGNORE)
    _write(agent_dir / ".aider.model.metadata.json", AGENT_METADATA)

    stub_dir = tmp_path / "bin"
    stub = stub_dir / "docker"
    _write(stub, STUB_DOCKER)
    stub.chmod(0o755)
    return sandbox, stub_dir


def _write_root_counterparts(sandbox: Path, files: dict[str, str]) -> None:
    """Write project-root counterpart files keyed by real file name."""
    for name, text in files.items():
        _write(sandbox / name, text)


def _launch(sandbox: Path, stub_dir: Path, tmp_path: Path) -> list[dict]:
    """Run the launcher once; return the `docker run` entries it logged."""
    log_path = stub_dir / "invocations.jsonl"
    before = (
        len(log_path.read_text(encoding="utf-8").splitlines())
        if log_path.exists()
        else 0
    )

    env = os.environ.copy()
    env["PATH"] = str(stub_dir) + os.pathsep + env.get("PATH", "")
    env["HOME"] = str(tmp_path / "home")
    env["TMPDIR"] = str(tmp_path / "tmp")
    env["AI_ASSISTANT_SESSION_ID"] = "s41-step5"
    env["STUB_LOG_PATH"] = str(log_path)
    (tmp_path / "home").mkdir(exist_ok=True)
    (tmp_path / "tmp").mkdir(exist_ok=True)

    result = subprocess.run(
        [sys.executable, str(sandbox / ".agent" / "ai_assistant.py")],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    entries = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()[before:]
        if line.strip()
    ]
    return [entry for entry in entries if entry["args"][:1] == ["run"]]


def _flag_target(run_entry: dict, flag: str) -> Path:
    args = run_entry["args"]
    return Path(args[args.index(flag) + 1])


def _flag_content(run_entry: dict, flag: str) -> str:
    content = run_entry["files"][flag]
    assert content is not None, f"the launcher pointed {flag} at a missing file"
    return content


def test_merge_case_all_counterparts_point_at_intermediates(tmp_path):
    sandbox, stub_dir = _make_sandbox(tmp_path)
    _write_root_counterparts(
        sandbox,
        {
            ".aider.conf.yml": ROOT_CONF,
            ".aider.model.settings.yml": ROOT_MODEL_SETTINGS,
            ".aiderignore": ROOT_IGNORE,
            ".aider.model.metadata.json": ROOT_METADATA,
        },
    )

    runs = _launch(sandbox, stub_dir, tmp_path)

    assert len(runs) == 1
    for name, flag in FLAG_BY_NAME.items():
        expected = sandbox / ".agent" / ".merged" / name
        assert _flag_target(runs[0], flag) == expected
        # The snapshot proves the intermediate existed with combined content.
        assert _flag_content(runs[0], flag) is not None


def test_conf_precedence_root_overrides_agent_default_retained(tmp_path):
    sandbox, stub_dir = _make_sandbox(tmp_path)
    _write_root_counterparts(sandbox, {".aider.conf.yml": ROOT_CONF})

    runs = _launch(sandbox, stub_dir, tmp_path)

    assert len(runs) == 1
    merged = _yaml_load(_flag_content(runs[0], "--config"))
    assert merged == {
        "model": "root-override",
        "map": {"refresh": True},
        "edit-format": "diff",
    }


def test_model_settings_precedence_root_entry_merge(tmp_path):
    sandbox, stub_dir = _make_sandbox(tmp_path)
    _write_root_counterparts(
        sandbox, {".aider.model.settings.yml": ROOT_MODEL_SETTINGS}
    )

    runs = _launch(sandbox, stub_dir, tmp_path)

    assert len(runs) == 1
    entries = _yaml_load(_flag_content(runs[0], "--model-settings-file"))
    by_name = {entry["name"]: entry for entry in entries}
    # Root override wins for the shared entry...
    assert by_name["provider/agent-a"]["extra_params"]["temperature"] == 0.9
    # ...the agent-only entry is retained...
    assert by_name["provider/agent-b"]["extra_params"]["max_tokens"] == 100
    # ...and the root-only entry is appended.
    assert by_name["provider/root-c"]["extra_params"]["max_tokens"] == 50


def test_metadata_precedence_root_overrides_agent_default_retained(tmp_path):
    sandbox, stub_dir = _make_sandbox(tmp_path)
    _write_root_counterparts(
        sandbox, {".aider.model.metadata.json": ROOT_METADATA}
    )

    runs = _launch(sandbox, stub_dir, tmp_path)

    assert len(runs) == 1
    merged = json.loads(_flag_content(runs[0], "--model-metadata-file"))
    assert merged["provider/agent-a"]["max_input_tokens"] == 2000
    assert merged["provider/agent-a"]["notes"] == "agent default"
    assert merged["provider/agent-b"]["max_input_tokens"] == 2000


def test_ignore_union_duplicates_counted_once(tmp_path):
    sandbox, stub_dir = _make_sandbox(tmp_path)
    _write_root_counterparts(sandbox, {".aiderignore": ROOT_IGNORE})

    runs = _launch(sandbox, stub_dir, tmp_path)

    assert len(runs) == 1
    patterns = _flag_content(runs[0], "--aiderignore").splitlines()
    # Agent patterns keep their order first, root-only patterns follow;
    # the duplicate *.log is counted once and comments/blanks are dropped.
    assert patterns == ["node_modules/", "*.log", "dist/", "build/"]


def test_no_counterparts_pass_through_agent_files(tmp_path):
    sandbox, stub_dir = _make_sandbox(tmp_path)

    runs = _launch(sandbox, stub_dir, tmp_path)

    assert len(runs) == 1
    for name, flag in FLAG_BY_NAME.items():
        assert _flag_target(runs[0], flag) == sandbox / ".agent" / name


def test_mixed_counterparts_merge_and_pass_through(tmp_path):
    sandbox, stub_dir = _make_sandbox(tmp_path)
    _write_root_counterparts(
        sandbox,
        {
            ".aider.conf.yml": ROOT_CONF,
            ".aiderignore": ROOT_IGNORE,
        },
    )

    runs = _launch(sandbox, stub_dir, tmp_path)

    assert len(runs) == 1
    # Counterparts present: merged intermediates.
    assert _flag_target(runs[0], "--config") == (
        sandbox / ".agent" / ".merged" / ".aider.conf.yml"
    )
    assert _flag_target(runs[0], "--aiderignore") == (
        sandbox / ".agent" / ".merged" / ".aiderignore"
    )
    # Counterparts absent: unchanged pass-through of the agent copies.
    assert _flag_target(runs[0], "--model-settings-file") == (
        sandbox / ".agent" / ".aider.model.settings.yml"
    )
    assert _flag_target(runs[0], "--model-metadata-file") == (
        sandbox / ".agent" / ".aider.model.metadata.json"
    )


def test_merge_is_deterministic_across_runs(tmp_path):
    sandbox, stub_dir = _make_sandbox(tmp_path)
    _write_root_counterparts(
        sandbox,
        {
            ".aider.conf.yml": ROOT_CONF,
            ".aider.model.settings.yml": ROOT_MODEL_SETTINGS,
            ".aiderignore": ROOT_IGNORE,
            ".aider.model.metadata.json": ROOT_METADATA,
        },
    )

    first_runs = _launch(sandbox, stub_dir, tmp_path)
    second_runs = _launch(sandbox, stub_dir, tmp_path)

    assert len(first_runs) == 1
    assert len(second_runs) == 1
    for flag in FLAG_BY_NAME.values():
        assert _flag_content(first_runs[0], flag) == _flag_content(
            second_runs[0], flag
        )
