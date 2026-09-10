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
