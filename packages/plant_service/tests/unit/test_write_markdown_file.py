"""Unit tests for ExportService._write_markdown_file YAML frontmatter."""
import yaml

from plant_service.service_layer.export_service import ExportService


def _parse_frontmatter(content: str) -> dict:
    """Extract and parse YAML frontmatter from written markdown content."""
    assert content.startswith("---\n")
    end = content.rindex("---\n")
    yaml_content = content[4:end]
    return yaml.safe_load(yaml_content)


class TestWriteMarkdownFile:
    def test_multiline_text(self, tmp_path):
        filepath = tmp_path / "log.md"
        text = "Line one\nLine two\n\nParagraph two"
        data = {"id": 1, "text": text}

        ExportService._write_markdown_file(filepath, data)

        parsed = _parse_frontmatter(filepath.read_text())
        assert parsed["id"] == 1
        assert parsed["text"] == text

    def test_yaml_boolean_like_strings(self, tmp_path):
        filepath = tmp_path / "log.md"
        data = {
            "fertilizer_type": "yes",
            "fertilizer_strength": "no",
            "event_type": "true",
            "plant_id": "false",
        }

        ExportService._write_markdown_file(filepath, data)

        parsed = _parse_frontmatter(filepath.read_text())
        assert parsed == data
        for value in parsed.values():
            assert isinstance(value, str)

    def test_colons_in_values(self, tmp_path):
        filepath = tmp_path / "log.md"
        data = {"text": "Note: watered at 10:30 AM"}

        ExportService._write_markdown_file(filepath, data)

        parsed = _parse_frontmatter(filepath.read_text())
        assert parsed["text"] == "Note: watered at 10:30 AM"

    def test_yaml_document_separator_in_content(self, tmp_path):
        filepath = tmp_path / "log.md"
        data = {"text": "Section break\n---\nMore notes"}

        ExportService._write_markdown_file(filepath, data)

        parsed = _parse_frontmatter(filepath.read_text())
        assert parsed["text"] == "Section break\n---\nMore notes"

    def test_skips_none_values(self, tmp_path):
        filepath = tmp_path / "log.md"
        data = {"id": 42, "text": "hello", "amount_ml": None}

        ExportService._write_markdown_file(filepath, data)

        parsed = _parse_frontmatter(filepath.read_text())
        assert parsed == {"id": 42, "text": "hello"}
        assert "amount_ml" not in parsed

    def test_preserves_integer_types(self, tmp_path):
        filepath = tmp_path / "log.md"
        data = {"id": 7, "level": 2, "amount_ml": 250}

        ExportService._write_markdown_file(filepath, data)

        content = filepath.read_text()
        parsed = _parse_frontmatter(content)
        assert parsed == data
        for key in ("id", "level", "amount_ml"):
            assert isinstance(parsed[key], int)
        assert "id: 7" in content
        assert "id: '7'" not in content
