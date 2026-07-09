"""Unit tests for SeedPacket domain model"""
import pytest

from plant_service.domain import SeedPacket


class TestSeedPacketGenerateId:
    def test_basic_format(self):
        sp = SeedPacket(id="", variety_name="Tomato", latin_name="Solanum lycopersicum")
        assert sp.generate_id(seq=1) == "SPKT-001"

    def test_sequence_padding(self):
        sp = SeedPacket(id="", variety_name="Tomato", latin_name="Solanum lycopersicum")
        assert sp.generate_id(seq=99) == "SPKT-099"

    def test_generate_id_rejects_seq_ge_1000(self):
        sp = SeedPacket(id="", variety_name="Tomato", latin_name="Solanum lycopersicum")
        with pytest.raises(ValueError, match="exceeds maximum of 999"):
            sp.generate_id(seq=1000)


class TestSeedPacketFindNextSequence:
    def test_empty_list(self):
        assert SeedPacket.find_next_sequence([]) == 1

    def test_existing_sequences(self):
        ids = ["SPKT-001", "SPKT-005", "SPKT-010"]
        assert SeedPacket.find_next_sequence(ids) == 11


class TestSeedPacketCreateFromDict:
    def test_valid_data(self):
        data = {"variety_name": "Tomato", "latin_name": "Solanum lycopersicum"}
        sp = SeedPacket.create_from_dict(data)
        assert sp.variety_name == "Tomato"
        assert sp.latin_name == "Solanum lycopersicum"
        assert sp.id == ""  # id generation happens in service layer

    def test_missing_required_field(self):
        with pytest.raises(ValueError, match="Missing required field"):
            SeedPacket.create_from_dict({"variety_name": "Tomato"})

    def test_missing_variety_name(self):
        with pytest.raises(ValueError, match="Missing required field"):
            SeedPacket.create_from_dict({"latin_name": "Solanum lycopersicum"})
