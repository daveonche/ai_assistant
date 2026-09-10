"""Story S1.4 Step 2 — Enable model settings configuration.

Verifies the Must Support items of Step 2 from
docs/analysis/S1.4-story-steps.md:
- Creation of a YAML file for model-specific settings
- Specification of parameters for model usage
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_SETTINGS = REPO_ROOT / ".agent" / ".aider.model.settings.yml"


def test_model_settings_file_exists_and_is_valid_yaml():
    """The model settings file exists and parses as valid YAML."""
    assert MODEL_SETTINGS.is_file(), f"missing model settings: {MODEL_SETTINGS}"
    loaded = yaml.safe_load(MODEL_SETTINGS.read_text(encoding="utf-8"))
    assert isinstance(loaded, list) and loaded, (
        "model settings must parse as a non-empty YAML list"
    )
    assert all(isinstance(entry, dict) for entry in loaded), (
        "each model settings entry must be a mapping"
    )
