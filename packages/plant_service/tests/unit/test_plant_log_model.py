"""Unit tests for PlantLogEntry domain model"""
import pytest

from plant_service.domain import PlantLogEntry


class TestPlantLogCreateFromDict:
    def test_valid_humidity(self):
        entry = PlantLogEntry.create_from_dict({
            "plant_id": "YEHA-2026-001",
            "event_type": "humidity",
            "level": 5,
        })
        assert entry.event_type == "humidity"
        assert entry.level == 5

    def test_valid_water(self):
        entry = PlantLogEntry.create_from_dict({
            "plant_id": "YEHA-2026-001",
            "event_type": "water",
            "amount_ml": 250,
        })
        assert entry.amount_ml == 250

    def test_valid_fertilizer(self):
        entry = PlantLogEntry.create_from_dict({
            "plant_id": "YEHA-2026-001",
            "event_type": "fertilizer",
            "fertilizer_type": "NPK",
            "fertilizer_strength": "5-10-5",
        })
        assert entry.fertilizer_type == "NPK"

    def test_valid_note(self):
        entry = PlantLogEntry.create_from_dict({
            "plant_id": "YEHA-2026-001",
            "event_type": "note",
            "text": "Plant is thriving",
        })
        assert entry.text == "Plant is thriving"

    def test_missing_plant_id(self):
        with pytest.raises(ValueError, match="Missing required field"):
            PlantLogEntry.create_from_dict({"event_type": "note"})

    def test_invalid_event_type(self):
        with pytest.raises(ValueError, match="Invalid event_type"):
            PlantLogEntry.create_from_dict({
                "plant_id": "YEHA-2026-001",
                "event_type": "invalid",
            })

    def test_humidity_out_of_range(self):
        with pytest.raises(ValueError, match="between 1 and 10"):
            PlantLogEntry.create_from_dict({
                "plant_id": "YEHA-2026-001",
                "event_type": "humidity",
                "level": 11,
            })

    def test_humidity_missing_level(self):
        with pytest.raises(ValueError, match="Missing required field: level"):
            PlantLogEntry.create_from_dict({
                "plant_id": "YEHA-2026-001",
                "event_type": "humidity",
            })

    def test_invalid_timestamp_format(self):
        with pytest.raises(ValueError, match="YYYY-MM-DDTHH:MM:SSZ"):
            PlantLogEntry.create_from_dict({
                "plant_id": "YEHA-2026-001",
                "event_type": "note",
                "text": "test",
                "timestamp": "2026-01-01",
            })

    def test_default_timestamp(self):
        entry = PlantLogEntry.create_from_dict({
            "plant_id": "YEHA-2026-001",
            "event_type": "note",
            "text": "test",
        })
        assert "T" in entry.timestamp and entry.timestamp.endswith("Z")

    def test_empty_plant_id(self):
        with pytest.raises(ValueError, match="non-empty string"):
            PlantLogEntry.create_from_dict({
                "plant_id": "",
                "event_type": "note",
                "text": "test",
            })
