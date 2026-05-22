"""Unit tests for Genus domain model"""
import pytest

from plant_service.domain import Genus


class TestGenusGenerateId:
    def test_basic_format(self):
        genus = Genus(id="", variety_name="Pepper", latin_name="Capsicum")
        assert genus.generate_id(seq=1) == "GENUS-001"

    def test_sequence_padding(self):
        genus = Genus(id="", variety_name="Tomato", latin_name="Solanum")
        assert genus.generate_id(seq=99) == "GENUS-099"


class TestGenusFindNextSequence:
    def test_empty_list(self):
        assert Genus.find_next_sequence([]) == 1

    def test_existing_sequences(self):
        ids = ["GENUS-001", "GENUS-005", "GENUS-010"]
        assert Genus.find_next_sequence(ids) == 11

    def test_other_ids_ignored(self):
        ids = ["SPKT-001", "YEHA-2026-001"]
        assert Genus.find_next_sequence(ids) == 1


class TestGenusCreateFromDict:
    def test_valid_data(self):
        data = {"variety_name": "Pepper", "latin_name": "Capsicum"}
        genus = Genus.create_from_dict(data)
        assert genus.variety_name == "Pepper"
        assert genus.latin_name == "Capsicum"

    def test_missing_variety_name(self):
        with pytest.raises(ValueError, match="Missing required field"):
            Genus.create_from_dict({"latin_name": "Capsicum"})

    def test_empty_variety_name(self):
        with pytest.raises(ValueError, match="Missing required field"):
            Genus.create_from_dict({"variety_name": "", "latin_name": "Capsicum"})
