"""Unit tests for Plant domain model"""
import pytest
from datetime import datetime

from plant_service.domain import Plant


class TestPlantMakeAbbrev:
    def test_two_word_name(self):
        assert Plant.make_abbrev("Yellow Habanero") == "YEHA"

    def test_single_word_name(self):
        assert Plant.make_abbrev("Tomato") == "TO"

    def test_long_name_truncated(self):
        assert len(Plant.make_abbrev("Very Long Variety Name")) == 4

    def test_numeric_name_fallback(self):
        result = Plant.make_abbrev("123 456")
        assert result == "123 "


class TestPlantGenerateId:
    def test_basic_format(self):
        plant = Plant(variety_name="Yellow Habanero", latin_name="Capsicum chinense")
        result = plant.generate_id("Yellow Habanero", "2026-03-15", seq=1)
        assert result == "YEHA-2026-001"

    def test_sequence_padding(self):
        plant = Plant(variety_name="Tomato", latin_name="Solanum lycopersicum")
        result = plant.generate_id("Tomato", "2026-01-01", seq=100)
        assert result == "TO-2026-100"

    def test_no_planting_date_uses_current_year(self):
        plant = Plant(variety_name="Pepper", latin_name="Capsicum annuum")
        result = plant.generate_id("Pepper", "", seq=5)
        current_year = datetime.now().year
        assert result == f"PE-{current_year}-005"


class TestPlantFindNextSequence:
    def test_empty_list(self):
        assert Plant.find_next_sequence("YEHA", 2026, []) == 1

    def test_existing_sequences(self):
        ids = ["YEHA-2026-001", "YEHA-2026-005", "YEHA-2025-003"]
        assert Plant.find_next_sequence("YEHA", 2026, ids) == 6

    def test_different_abbrev(self):
        ids = ["TOMA-2026-010"]
        assert Plant.find_next_sequence("YEHA", 2026, ids) == 1


class TestPlantCreateFromDict:
    def test_valid_data(self):
        data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "planting_date": "2026-03-15",
        }
        plant = Plant.create_from_dict(data)
        assert plant.variety_name == "Yellow Habanero"
        assert plant.latin_name == "Capsicum chinense"
        assert plant.planting_date == "2026-03-15"
        assert plant.id == ""  # id generation happens in service layer

    def test_valid_data_with_id(self):
        data = {
            "id": "YEHA-2026-001",
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "planting_date": "2026-03-15",
        }
        plant = Plant.create_from_dict(data)
        assert plant.id == "YEHA-2026-001"

    def test_missing_required_field(self):
        with pytest.raises(ValueError, match="Missing required field"):
            Plant.create_from_dict({"variety_name": "Tomato"})

    def test_invalid_genus_id_format(self):
        with pytest.raises(ValueError, match="GENUS-NNN"):
            Plant.create_from_dict({
                "variety_name": "Tomato",
                "latin_name": "Solanum lycopersicum",
                "planting_date": "2026-01-01",
                "genus_id": "INVALID",
            })

    def test_valid_genus_id(self):
        plant = Plant.create_from_dict({
            "variety_name": "Tomato",
            "latin_name": "Solanum lycopersicum",
            "planting_date": "2026-01-01",
            "genus_id": "GENUS-001",
        })
        assert plant.genus_id == "GENUS-001"

    def test_unknown_genus_id_allowed(self):
        plant = Plant.create_from_dict({
            "variety_name": "Tomato",
            "latin_name": "Solanum lycopersicum",
            "planting_date": "2026-01-01",
            "genus_id": "unknown",
        })
        assert plant.genus_id == "unknown"

    def test_invalid_date_format(self):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            Plant.create_from_dict({
                "variety_name": "Tomato",
                "latin_name": "Solanum lycopersicum",
                "planting_date": "01-01-2026",
            })

    def test_invalid_seed_packet_id(self):
        with pytest.raises(ValueError, match="SPKT-NNN"):
            Plant.create_from_dict({
                "variety_name": "Tomato",
                "latin_name": "Solanum lycopersicum",
                "planting_date": "2026-01-01",
                "seed_packet_id": "INVALID",
            })
