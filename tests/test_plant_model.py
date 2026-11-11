"""Unit tests for date handling in the Markdown-based Plant model"""

from datetime import date

from commands.plant_model import Plant, load_plant_from_file


class TestPlantDateObjectHandling:
    def test_planting_date_object_normalized_to_iso_string(self):
        plant = Plant(
            {
                "id": "YHAB-2026-001",
                "variety_name": "Yellow Habanero",
                "latin_name": "Capsicum chinense",
                "planting_date": date(2026, 3, 15),
            }
        )
        assert plant.data["planting_date"] == "2026-03-15"

    def test_to_markdown_round_trip_with_date_object(self, tmp_path):
        plant = Plant(
            {
                "id": "YHAB-2026-001",
                "variety_name": "Yellow Habanero",
                "latin_name": "Capsicum chinense",
                "planting_date": date(2026, 3, 15),
            }
        )
        filepath = tmp_path / "YHAB-2026-001.md"
        filepath.write_text(plant.to_markdown())

        reloaded = load_plant_from_file(filepath)
        assert reloaded.data["planting_date"] == "2026-03-15"
