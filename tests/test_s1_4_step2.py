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


def test_entries_specify_model_names():
    """Each model settings entry specifies a model name."""
    loaded = yaml.safe_load(MODEL_SETTINGS.read_text(encoding="utf-8"))
    for entry in loaded:
        assert "name" in entry, (
            f"model settings entry missing 'name': {entry}"
        )
        assert isinstance(entry["name"], str) and entry["name"].strip(), (
            f"model name must be a non-empty string: {entry.get('name')!r}"
        )


def test_entries_specify_model_usage_parameters():
    """Each model settings entry specifies parameters for model
    usage beyond the model name (e.g., edit_format, extra_params,
    temperature, max_tokens)."""
    loaded = yaml.safe_load(MODEL_SETTINGS.read_text(encoding="utf-8"))
    usage_parameter_keys = {
        "edit_format", "extra_params", "temperature", "max_tokens"
    }
    for entry in loaded:
        name = entry.get("name", "<unnamed>")
        present = usage_parameter_keys & entry.keys()
        assert present, (
            f"model settings entry {name!r} must specify at least one "
            f"usage parameter from: {sorted(usage_parameter_keys)}"
        )
        # extra_params, if specified, must be a mapping
        if "extra_params" in entry:
            assert isinstance(entry["extra_params"], dict), (
                f"extra_params for {name!r} must be a mapping"
            )
