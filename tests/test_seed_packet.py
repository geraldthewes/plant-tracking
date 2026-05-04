"""
Test suite for seed packet model
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path


class TestSeedPacketModel(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.test_packets_dir = self.test_db / "seed_packets"
        self.test_packets_dir.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        from commands.seed_packet_model import SeedPacket

        self.SeedPacket = SeedPacket

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _packet_data(self, **overrides):
        """Create seed packet data with required fields."""
        data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
        }
        data.update(overrides)
        return data

    def _full_packet_data(self, **overrides):
        """Create seed packet data with all fields."""
        data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "brand": "Gardners Basics",
            "days_to_maturity": "80-100",
            "germination_time": "7-21",
            "planting_depth": "0.25",
            "spacing": "12-18",
            "sun_requirements": "Full Sun",
            "indoor_start_time": "8-10 weeks before last frost",
        }
        data.update(overrides)
        return data

    def test_creation_required_fields(self):
        """Test creating a seed packet with only required fields."""
        data = self._packet_data()
        packet = self.SeedPacket(data)
        self.assertEqual(packet.data["variety_name"], "Yellow Habanero")
        self.assertEqual(packet.data["latin_name"], "Capsicum chinense")
        self.assertIn("id", packet.data)

    def test_creation_full_data(self):
        """Test creating a seed packet with all fields."""
        data = self._full_packet_data()
        packet = self.SeedPacket(data)
        self.assertEqual(packet.data["brand"], "Gardners Basics")
        self.assertEqual(packet.data["days_to_maturity"], "80-100")

    def test_id_format(self):
        """Test that IDs follow SPKT-NNN format."""
        import re

        data = self._packet_data()
        packet = self.SeedPacket(data)
        self.assertRegex(packet.data["id"], r"^SPKT-\d{3}$")

    def test_id_sequencing(self):
        """Test that IDs increment correctly."""
        data1 = self._packet_data(variety_name="Avocado", latin_name="Persea americana")
        packet1 = self.SeedPacket(data1)
        filepath = self.test_packets_dir / f"{packet1.data['id']}.md"
        with open(filepath, "w") as f:
            f.write(packet1.to_markdown())

        data2 = self._packet_data(
            variety_name="Tomato", latin_name="Solanum lycopersicum"
        )
        packet2 = self.SeedPacket(data2)

        seq1 = int(packet1.data["id"].split("-")[1])
        seq2 = int(packet2.data["id"].split("-")[1])
        self.assertEqual(seq2, seq1 + 1)

    def test_markdown_roundtrip(self):
        """Test save then load preserves data."""
        data = self._full_packet_data()
        packet = self.SeedPacket(data)
        filepath = self.test_packets_dir / f"{packet.data['id']}.md"

        with open(filepath, "w") as f:
            f.write(packet.to_markdown())

        from commands.seed_packet_model import load_from_file

        loaded = load_from_file(filepath)

        self.assertEqual(loaded.data["variety_name"], packet.data["variety_name"])
        self.assertEqual(loaded.data["latin_name"], packet.data["latin_name"])
        self.assertEqual(loaded.data["brand"], packet.data["brand"])
        self.assertEqual(loaded.data["id"], packet.data["id"])

    def test_markdown_output_format(self):
        """Test that markdown output has correct structure."""
        data = self._full_packet_data()
        packet = self.SeedPacket(data)
        md = packet.to_markdown()

        self.assertIn("---", md)
        self.assertIn("variety_name: Yellow Habanero", md)
        self.assertIn("# Seed Packet: Yellow Habanero", md)
        self.assertIn(packet.data["id"], md)
        self.assertIn("created_at:", md)
        self.assertIn("updated_at:", md)

    def test_missing_required_field_variety(self):
        """Test that missing variety_name raises ValueError."""
        data = {"latin_name": "Capsicum chinense"}
        with self.assertRaises(ValueError) as ctx:
            self.SeedPacket(data)
        self.assertIn("variety_name", str(ctx.exception))

    def test_missing_required_field_latin(self):
        """Test that missing latin_name raises ValueError."""
        data = {"variety_name": "Yellow Habanero"}
        with self.assertRaises(ValueError) as ctx:
            self.SeedPacket(data)
        self.assertIn("latin_name", str(ctx.exception))


class TestFindMatching(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.test_packets_dir = self.test_db / "seed_packets"
        self.test_packets_dir.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        from commands.seed_packet_model import SeedPacket, find_matching

        self.SeedPacket = SeedPacket
        self.find_matching = find_matching

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_find_matching_returns_packet(self):
        """Test that find_matching returns the correct packet."""
        data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "brand": "Gardners Basics",
        }
        packet = self.SeedPacket(data)
        filepath = self.test_packets_dir / f"{packet.data['id']}.md"
        with open(filepath, "w") as f:
            f.write(packet.to_markdown())

        result = self.find_matching("Yellow Habanero", "Capsicum chinense")
        self.assertIsNotNone(result)
        self.assertEqual(result.data["brand"], "Gardners Basics")

    def test_find_matching_returns_none(self):
        """Test that find_matching returns None when no match."""
        result = self.find_matching("Nonexistent", "Plantae nulla")
        self.assertIsNone(result)

    def test_find_matching_exact(self):
        """Test that find_matching requires exact match on both fields."""
        data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
        }
        packet = self.SeedPacket(data)
        filepath = self.test_packets_dir / f"{packet.data['id']}.md"
        with open(filepath, "w") as f:
            f.write(packet.to_markdown())

        result = self.find_matching("Yellow Habanero", "Capsicum annuum")
        self.assertIsNone(result)

        result = self.find_matching("Red Habanero", "Capsicum chinense")
        self.assertIsNone(result)


class TestListAll(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.test_packets_dir = self.test_db / "seed_packets"
        self.test_packets_dir.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        from commands.seed_packet_model import SeedPacket, list_all

        self.SeedPacket = SeedPacket
        self.list_all = list_all

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_list_all_empty(self):
        """Test that list_all returns empty list when no packets exist."""
        result = self.list_all()
        self.assertEqual(result, [])

    def test_list_all_returns_all(self):
        """Test that list_all returns all packets."""
        for name, latin in [
            ("Avocado", "Persea americana"),
            ("Tomato", "Solanum lycopersicum"),
        ]:
            data = {"variety_name": name, "latin_name": latin}
            packet = self.SeedPacket(data)
            filepath = self.test_packets_dir / f"{packet.data['id']}.md"
            with open(filepath, "w") as f:
                f.write(packet.to_markdown())

        result = self.list_all()
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
