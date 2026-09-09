"""Story S1.4 Step 1 — Enable Aider configuration file creation.

Verifies the Must Support items of Step 1 from
docs/analysis/S1.4-story-steps.md:
- Creation of a YAML configuration file for Aider
- Specification of necessary Aider settings (e.g., default model,
  auto-commits)
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
AIDER_CONFIG = REPO_ROOT / ".agent" / ".aider.conf.yml"


def test_aider_config_yaml_file_exists_and_is_valid_yaml():
    """The Aider configuration file exists and parses as valid YAML."""
    assert AIDER_CONFIG.is_file(), f"missing Aider config: {AIDER_CONFIG}"
    loaded = yaml.safe_load(AIDER_CONFIG.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict), "aider config must parse as a YAML mapping"
