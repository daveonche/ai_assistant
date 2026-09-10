from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_license_file_declares_license_terms():
    # the license file exists at the project root and is non-empty
    license_path = PROJECT_ROOT / "LICENSE"
    assert license_path.is_file(), "LICENSE is missing from the project root"
    text = license_path.read_text()
    assert text.strip(), "LICENSE is empty"

    # the license states its terms: identifier, copyright, permission
    # grant, and warranty disclaimer
    assert "MIT License" in text, "LICENSE does not state the MIT license terms"
    assert "Copyright (c)" in text, "LICENSE has no copyright notice"
    assert "Permission is hereby granted" in text, (
        "LICENSE has no permission grant"
    )
    assert "AS IS" in text, "LICENSE has no warranty disclaimer"


def test_readme_describes_project_purpose():
    # the readme exists at the project root and is non-empty
    readme_path = PROJECT_ROOT / "README.md"
    assert readme_path.is_file(), "README.md is missing from the project root"
    text = readme_path.read_text()
    assert text.strip(), "README.md is empty"

    # exactly one H1 title
    h1_lines = [
        line for line in text.splitlines() if line.startswith("# ")
    ]
    assert len(h1_lines) == 1, (
        f"README.md must have exactly one H1 title, found {len(h1_lines)}"
    )

    # the opening prose (before the first ## section) describes the
    # project purpose: wrapping/orchestrating the Aider assistant
    opening = text.split("## ", 1)[0].lower()
    assert "aider" in opening, (
        "README.md opening prose does not mention the Aider assistant"
    )
    assert any(
        word in opening for word in ("wrapper", "orchestrat", "pipeline")
    ), (
        "README.md opening prose does not describe the wrapper/orchestrator purpose"
    )
