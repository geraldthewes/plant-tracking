#!/usr/bin/env python3
"""
Generate rule.json from Markdown files in the rules/ directory.

Usage:
    python generate-rules.py
"""

import json
from pathlib import Path

RULES_DIR = Path(__file__).parent / "rules"
OUTPUT_FILE = Path(__file__).parent / "rule.json"


def load_rule_file(path: Path) -> str:
    """Load a markdown rule file and return its content as a clean string."""
    content = path.read_text(encoding="utf-8").strip()
    return content.replace("\r\n", "\n")


def load_secure_coding_rules() -> str:
    """Load and combine all Python secure coding rule files."""
    secure_dir = RULES_DIR / "python-secure-coding"
    files = sorted(secure_dir.glob("*.md"))
    contents = [load_rule_file(f) for f in files]
    return "\n\n---\n\n".join(contents)


def main():
    rules = []

    # Main Python rules
    python_rule = load_rule_file(RULES_DIR / "python.md")
    rules.append({
        "path": "**/*.py",
        "rule": python_rule
    })

    # FastAPI specific rules
    fastapi_rule = load_rule_file(RULES_DIR / "fastapi.md")
    rules.append({
        "path": "**/routers/**/*.py",
        "rule": fastapi_rule
    })
    rules.append({
        "path": "**/main.py",
        "rule": fastapi_rule
    })

    # Security rules
    security_rule = load_rule_file(RULES_DIR / "security.md")
    rules.append({
        "path": "**/*.py",
        "rule": security_rule
    })

    # Testing rules
    testing_rule = load_rule_file(RULES_DIR / "testing.md")
    rules.append({
        "path": "**/test_*.py",
        "rule": testing_rule
    })
    rules.append({
        "path": "**/tests/**/*.py",
        "rule": testing_rule
    })

    # Google Python Style Guide rules (citable: PY-LANG-*, PY-STY-*)
    style_rule = load_rule_file(RULES_DIR / "python-style.md")
    rules.append({
        "path": "**/*.py",
        "rule": style_rule
    })

    # OpenSSF Secure Coding Guide rules (citable: PYSCG-*)
    secure_coding_rule = load_secure_coding_rules()
    rules.append({
        "path": "**/*.py",
        "rule": secure_coding_rule
    })

    output = {"rules": rules}

    OUTPUT_FILE.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print(f"Generated {OUTPUT_FILE} with {len(rules)} rules.")


if __name__ == "__main__":
    main()