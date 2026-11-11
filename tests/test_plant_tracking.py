"""
Test suite for plant tracking system
"""

import io
import logging
import os
import re
import shutil
import tempfile
import unittest
from unittest import mock
from datetime import date, datetime, timezone
from pathlib import Path


class TestPlantModel(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()

        # Save original and set test database
        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        # Import after setting env var so modules pick up the test dir
        from commands.plant_model import Plant

        self.Plant = Plant

    def tearDown(self):
        # Restore original database dir
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)

        # Clean up test directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _required_plant_data(self, **overrides):
        """Create plant data with the three required label fields."""
        data = {
            "variety_name": "Test Plant",
            "latin_name": "Testus plantus",
            "planting_date": "2026-05-01",
        }
        data.update(overrides)
        return data

    def _full_plant_data(self, variety_name="Test Plant", **overrides):
        """Create plant data with all optional fields."""
        data = {
            "variety_name": variety_name,
            "latin_name": "Testus plantus",
            "brand": "Test Brand",
            "days_to_maturity": 60,
            "germination_time": "5-10 days",
            "planting_depth": "0.5 inches",
            "spacing": "12 inches",
            "sun_requirements": "Partial sun",
            "indoor_start_time": "6 weeks",
            "planting_date": "2026-05-01",
        }
        data.update(overrides)
        return data

    def test_plant_creation_required_fields(self):
        """Test creating a plant with only required fields"""
        plant_data = self._required_plant_data(
            variety_name="Habanero",
            latin_name="Capsicum chinense",
            planting_date="2026-05-01",
        )
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data["variety_name"], "Habanero")
        self.assertTrue(plant.data["id"].startswith("HA"))

    def test_plant_creation_valid_data(self):
        """Test creating a plant with all data"""
        plant_data = self._full_plant_data(
            variety_name="Yellow Habanero", brand="Burpee"
        )
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data["variety_name"], "Yellow Habanero")
        self.assertTrue(plant.data["id"].startswith("YEHA"))
        self.assertEqual(plant.data["brand"], "Burpee")

    def test_plant_id_generation_format(self):
        """Test that plant IDs follow VARIETY-YYYY-SEQ format"""
        plant_data = self._required_plant_data(
            variety_name="Habanero",
            latin_name="Capsicum chinense",
            planting_date="2026-05-01",
        )
        plant = self.Plant(plant_data)
        pattern = r"^[A-Z]{2,4}-\d{4}-\d{3}$"
        self.assertRegex(plant.data["id"], pattern)

    def test_plant_id_generation_haby(self):
        """Test ID abbreviation for multi-word variety names"""
        plant_data = self._required_plant_data(
            variety_name="Yellow Habanero",
            latin_name="Capsicum chinense",
            planting_date="2026-05-01",
        )
        plant = self.Plant(plant_data)
        self.assertTrue(plant.data["id"].startswith("YEHA"))

    def test_plant_id_generation_single_word(self):
        """Test ID abbreviation for single-word variety names"""
        plant_data = self._required_plant_data(
            variety_name="Habanero",
            latin_name="Capsicum chinense",
            planting_date="2026-05-01",
        )
        plant = self.Plant(plant_data)
        self.assertTrue(plant.data["id"].startswith("HA"))

    def test_plant_markdown_output(self):
        """Test that plant converts to markdown correctly"""
        plant_data = self._full_plant_data(variety_name="Test Plant")
        plant = self.Plant(plant_data)
        markdown = plant.to_markdown()

        self.assertIn("---", markdown)
        self.assertIn("variety_name: Test Plant", markdown)
        self.assertIn("# Plant Record for Test Plant", markdown)
        self.assertIn(f'*ID: {plant.data["id"]}*', markdown)
        self.assertIn("created_at:", markdown)
        self.assertIn("updated_at:", markdown)

    def test_plant_markdown_required_only(self):
        """Test markdown output with only required fields"""
        plant_data = self._required_plant_data(variety_name="Basic Plant")
        plant = self.Plant(plant_data)
        markdown = plant.to_markdown()

        self.assertIn("---", markdown)
        self.assertIn("variety_name: Basic Plant", markdown)
        self.assertIn(f'*ID: {plant.data["id"]}*', markdown)

    def test_plant_missing_required_field(self):
        """Test that missing required field raises ValueError"""
        with self.assertRaises(ValueError) as ctx:
            self.Plant({})
        self.assertIn("Missing required field", str(ctx.exception))

    def test_plant_days_to_maturity_range(self):
        """Test that days_to_maturity accepts range strings"""
        plant_data = self._required_plant_data(days_to_maturity="60-75")
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data["days_to_maturity"], "60-75")

    def test_plant_days_to_maturity_string(self):
        """Test that days_to_maturity accepts single value strings"""
        plant_data = self._required_plant_data(days_to_maturity="90")
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data["days_to_maturity"], "90")

    def test_plant_invalid_date_format(self):
        """Test that invalid date format raises ValueError"""
        plant_data = self._required_plant_data(planting_date="05-01-2026")
        with self.assertRaises(ValueError):
            self.Plant(plant_data)

    def test_record_only_fields_optional(self):
        """Test that record-only fields are accepted without error"""
        plant_data = self._required_plant_data(
            brand="Test Brand",
            days_to_maturity="90",
        )
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data["brand"], "Test Brand")
        self.assertEqual(plant.data["days_to_maturity"], "90")

    def test_id_sequencing(self):
        """Test that sequence numbers increment correctly"""
        data1 = self._required_plant_data(variety_name="Test Plant")
        plant1 = self.Plant(data1)
        # Save to database so next plant sees it
        filepath = self.test_db / f"{plant1.data['id']}.md"
        with open(filepath, "w") as f:
            f.write(plant1.to_markdown())

        data2 = self._required_plant_data(variety_name="Test Plant")
        plant2 = self.Plant(data2)

        seq1 = int(plant1.data["id"].split("-")[2])
        seq2 = int(plant2.data["id"].split("-")[2])
        self.assertEqual(seq2, seq1 + 1)

    def test_load_plant_from_file(self):
        """Test loading a plant record from a markdown file"""
        plant_data = self._full_plant_data(variety_name="Loaded Plant")
        plant = self.Plant(plant_data)
        filepath = self.test_db / f"{plant.data['id']}.md"

        with open(filepath, "w") as f:
            f.write(plant.to_markdown())

        from commands.plant_model import load_plant_from_file

        loaded = load_plant_from_file(filepath)
        self.assertEqual(loaded.data["variety_name"], "Loaded Plant")
        self.assertEqual(loaded.data["id"], plant.data["id"])

    def test_load_required_only_from_file(self):
        """Test loading a plant record with only required fields"""
        plant_data = self._required_plant_data(variety_name="Required Plant")
        plant = self.Plant(plant_data)
        filepath = self.test_db / f"{plant.data['id']}.md"

        with open(filepath, "w") as f:
            f.write(plant.to_markdown())

        from commands.plant_model import load_plant_from_file

        loaded = load_plant_from_file(filepath)
        self.assertEqual(loaded.data["variety_name"], "Required Plant")
        self.assertEqual(loaded.data["id"], plant.data["id"])

    def test_load_invalid_file(self):
        """Test loading an invalid file raises error"""
        invalid_file = self.test_db / "invalid.md"
        with open(invalid_file, "w") as f:
            f.write("no frontmatter here")

        from commands.plant_model import load_plant_from_file

        with self.assertRaises(ValueError):
            load_plant_from_file(invalid_file)

    def test_id_year_from_planting_date_past_year(self):
        """Test that ID year comes from planting_date, not current year."""
        plant_data = self._required_plant_data(
            variety_name="Yellow Habanero",
            latin_name="Capsicum chinense",
            planting_date="2024-05-01",
        )
        plant = self.Plant(plant_data)
        self.assertIn("-2024-", plant.data["id"])

    def test_id_year_from_planting_date_future_year(self):
        """Test that ID year comes from planting_date for future dates."""
        next_year = datetime.now(timezone.utc).year + 1
        plant_data = self._required_plant_data(
            variety_name="Tomato",
            latin_name="Solanum lycopersicum",
            planting_date=f"{next_year}-06-01",
        )
        plant = self.Plant(plant_data)
        self.assertIn(f"-{next_year}-", plant.data["id"])


class TestPlantSeedPacketReference(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.test_packets_dir = self.test_db / "seed_packets"
        self.test_packets_dir.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        from commands.plant_model import Plant

        self.Plant = Plant

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_plant_with_seed_packet_id_saves_loads(self):
        """Test that a plant with seed_packet_id saves and loads correctly."""
        plant_data = {
            "variety_name": "Test Plant",
            "latin_name": "Testus plantus",
            "planting_date": "2026-05-01",
            "seed_packet_id": "SPKT-001",
        }
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data["seed_packet_id"], "SPKT-001")

        filepath = self.test_db / f"{plant.data['id']}.md"
        with open(filepath, "w") as f:
            f.write(plant.to_markdown())

        from commands.plant_model import load_plant_from_file

        loaded = load_plant_from_file(filepath)
        self.assertEqual(loaded.data["seed_packet_id"], "SPKT-001")

    def test_plant_with_unknown_seed_packet_id(self):
        """Test that seed_packet_id of 'unknown' is valid."""
        plant_data = {
            "variety_name": "Test Plant",
            "latin_name": "Testus plantus",
            "planting_date": "2026-05-01",
            "seed_packet_id": "unknown",
        }
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data["seed_packet_id"], "unknown")
        self.assertIsNone(plant.get_seed_packet())

    def test_get_seed_packet_resolves_reference(self):
        """Test that get_seed_packet resolves to the correct SeedPacket."""
        from commands.seed_packet_model import SeedPacket

        packet_data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "brand": "Gardners Basics",
        }
        packet = SeedPacket(packet_data)
        packet_path = self.test_packets_dir / f"{packet.data['id']}.md"
        with open(packet_path, "w") as f:
            f.write(packet.to_markdown())

        plant_data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "planting_date": "2026-05-01",
            "seed_packet_id": packet.data["id"],
        }
        plant = self.Plant(plant_data)
        resolved = plant.get_seed_packet()
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.data["brand"], "Gardners Basics")

    def test_get_seed_packet_missing_reference(self):
        """Test that get_seed_packet returns None for missing packet."""
        plant_data = {
            "variety_name": "Test Plant",
            "latin_name": "Testus plantus",
            "planting_date": "2026-05-01",
            "seed_packet_id": "SPKT-999",
        }
        plant = self.Plant(plant_data)
        self.assertIsNone(plant.get_seed_packet())


class TestLabelGeneration(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        from commands.plant_model import Plant

        self.Plant = Plant

        # Create a test plant with full data
        plant_data = {
            "variety_name": "Test Variety",
            "latin_name": "Testus varietyus",
            "brand": "Test Brand",
            "days_to_maturity": 75,
            "germination_time": "7 days",
            "planting_depth": "0.25 inches",
            "spacing": "10 inches",
            "sun_requirements": "Full sun",
            "indoor_start_time": "4 weeks",
            "planting_date": "2026-06-01",
        }
        plant = self.Plant(plant_data)
        plant_file = self.test_db / f"{plant.data['id']}.md"
        with open(plant_file, "w") as f:
            f.write(plant.to_markdown())
        self.test_plant_id = plant.data["id"]

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_label_dimensions(self):
        """Test that generated label has correct dimensions"""
        from commands.label_generator import create_label
        from PIL import Image

        label_path = self.test_dir / "test_label.png"
        generated_path = create_label(self.test_plant_id, label_path)

        self.assertTrue(generated_path.exists())

        img = Image.open(generated_path)
        width, height = img.size

        expected_width = int(40 * 203 / 25.4)  # ~319px
        expected_height = int(30 * 203 / 25.4)  # ~236px

        tolerance = 0.1
        self.assertGreaterEqual(width, int(expected_width * (1 - tolerance)))
        self.assertLessEqual(width, int(expected_width * (1 + tolerance)))
        self.assertGreaterEqual(height, int(expected_height * (1 - tolerance)))
        self.assertLessEqual(height, int(expected_height * (1 + tolerance)))

    def test_label_qr_code(self):
        """Test that QR code is rendered on the label"""
        from commands.label_generator import create_label
        from PIL import Image

        label_path = self.test_dir / "test_qr_label.png"
        create_label(self.test_plant_id, label_path)

        img = Image.open(label_path).convert("RGB")
        pixels = list(img.getdata())

        # Count black pixels in the image (QR code area is on the right side)
        black_count = sum(1 for r, g, b in pixels if r < 100 and g < 100 and b < 100)

        # Labels are mostly white; check for presence of rendered content
        self.assertGreater(
            black_count, 100, "Expected rendered QR code and text content"
        )

    def test_label_missing_plant(self):
        """Test that missing plant raises FileNotFoundError"""
        from commands.label_generator import create_label

        with self.assertRaises(FileNotFoundError):
            create_label("NONEXISTENT-2026-001")


class TestPrinter(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        from commands.plant_model import Plant

        self.Plant = Plant

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @mock.patch("commands.printer._select_printer")
    def test_print_missing_plant(self, mock_select):
        """Test that printing a missing plant returns False"""
        mock_select.return_value = None
        from commands.printer import print_label

        result = print_label("NONEXISTENT-2026-001")
        self.assertFalse(result)

    @mock.patch("commands.printer._select_printer")
    def test_print_nonexistent_file(self, mock_select):
        """Test that printing a nonexistent file returns False"""
        mock_select.return_value = None
        from commands.printer import print_label

        result = print_label("/tmp/does_not_exist.png")
        self.assertFalse(result)


class TestCreatePlantFlow(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.test_packets_dir = self.test_db / "seed_packets"
        self.test_packets_dir.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @mock.patch(
        "builtins.input",
        side_effect=["Yellow Habanero", "Capsicum chinense", "Y", "2026-05-01"],
    )
    def test_create_plant_with_existing_packet(self, mock_input):
        """Test create-plant uses existing seed packet when match found."""
        from commands.seed_packet_model import SeedPacket
        from commands import plant_tracking_cli

        plant_tracking_cli.DATABASE_DIR = self.test_db
        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir

        # Create an existing seed packet
        packet = SeedPacket(
            {"variety_name": "Yellow Habanero", "latin_name": "Capsicum chinense"}
        )
        fp = self.test_packets_dir / f"{packet.data['id']}.md"
        with open(fp, "w") as f:
            f.write(packet.to_markdown())

        plant_tracking_cli.create_plant(type("Args", (), {})())

        plant_files = list(self.test_db.glob("*.md"))
        self.assertEqual(len(plant_files), 1)

        from commands.plant_model import load_plant_from_file

        loaded = load_plant_from_file(plant_files[0])
        self.assertEqual(loaded.data["seed_packet_id"], packet.data["id"])

    @mock.patch(
        "builtins.input",
        side_effect=[
            "Yellow Habanero",
            "Capsicum chinense",
            "N",
            "C",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "2026-05-01",
        ],
    )
    def test_create_plant_skip_packet_unknown(self, mock_input):
        """Test create-plant with skip path sets seed_packet_id to unknown."""
        from commands import plant_tracking_cli

        plant_tracking_cli.DATABASE_DIR = self.test_db
        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir

        plant_tracking_cli.create_plant(type("Args", (), {})())

        plant_files = list(self.test_db.glob("*.md"))
        self.assertEqual(len(plant_files), 1)

        from commands.plant_model import load_plant_from_file

        loaded = load_plant_from_file(plant_files[0])
        self.assertEqual(loaded.data["seed_packet_id"], "unknown")

    @mock.patch(
        "builtins.input",
        side_effect=[
            "Yellow Habanero",
            "Capsicum chinense",
            "N",
            "A",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "2026-05-01",
        ],
    )
    def test_create_plant_create_new_packet(self, mock_input):
        """Test create-plant creates new seed packet inline."""
        from commands import plant_tracking_cli

        plant_tracking_cli.DATABASE_DIR = self.test_db
        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir

        plant_tracking_cli.create_plant(type("Args", (), {})())

        plant_files = list(self.test_db.glob("*.md"))
        packet_files = list(self.test_packets_dir.glob("*.md"))

        self.assertEqual(len(plant_files), 1)
        self.assertEqual(len(packet_files), 1)

        from commands.plant_model import load_plant_from_file

        loaded = load_plant_from_file(plant_files[0])
        self.assertEqual(loaded.data["seed_packet_id"], packet_files[0].stem)

    @mock.patch(
        "builtins.input",
        side_effect=[
            "Yellow Habanero",
            "Capsicum chinense",
            "N",
            "B",
            "SPKT-001",
            "2026-05-01",
        ],
    )
    def test_create_plant_select_existing_packet(self, mock_input):
        """Test create-plant selects existing packet from list."""
        from commands.seed_packet_model import SeedPacket
        from commands import plant_tracking_cli

        plant_tracking_cli.DATABASE_DIR = self.test_db
        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir

        # Create a packet with a DIFFERENT variety so auto-match doesn't trigger
        packet = SeedPacket(
            {
                "variety_name": "Red Habanero",
                "latin_name": "Capsicum chinense",
                "id": "SPKT-001",
            }
        )
        fp = self.test_packets_dir / "SPKT-001.md"
        with open(fp, "w") as f:
            f.write(packet.to_markdown())

        plant_tracking_cli.create_plant(type("Args", (), {})())

        plant_files = list(self.test_db.glob("*.md"))
        self.assertEqual(len(plant_files), 1)

        from commands.plant_model import load_plant_from_file

        loaded = load_plant_from_file(plant_files[0])
        self.assertEqual(loaded.data["seed_packet_id"], "SPKT-001")


class TestSeedPacketCLI(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.test_packets_dir = self.test_db / "seed_packets"
        self.test_packets_dir.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @mock.patch(
        "builtins.input",
        side_effect=[
            "Yellow Habanero",
            "Capsicum chinense",
            "Gardners Basics",
            "80-100",
            "7-21",
            "0.25",
            "12-18",
            "Full Sun",
            "8-10 weeks",
        ],
    )
    def test_create_seed_packet_command(self, mock_input):
        """Test create-seed-packet subcommand creates a record."""
        from commands import plant_tracking_cli

        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir
        plant_tracking_cli.create_seed_packet(type("Args", (), {})())

        files = list(self.test_packets_dir.glob("*.md"))
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].name.startswith("SPKT-"))

    @mock.patch(
        "builtins.input",
        side_effect=[
            "Yellow Habanero",
            "Capsicum chinense",
            "y",
            "Gardners Basics",
            "80-100",
            "7-21",
            "0.25",
            "12-18",
            "Full Sun",
            "8-10 weeks",
        ],
    )
    def test_create_seed_packet_duplicate_warning(self, mock_input):
        """Test create-seed-packet warns on duplicate and creates on confirm."""
        from commands.seed_packet_model import SeedPacket
        from commands import plant_tracking_cli

        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir

        first = SeedPacket(
            {"variety_name": "Yellow Habanero", "latin_name": "Capsicum chinense"}
        )
        fp = self.test_packets_dir / f"{first.data['id']}.md"
        with open(fp, "w") as f:
            f.write(first.to_markdown())

        plant_tracking_cli.create_seed_packet(type("Args", (), {})())

        files = list(self.test_packets_dir.glob("*.md"))
        self.assertEqual(len(files), 2)

    def test_list_seed_packets_command(self):
        """Test list-seed-packets shows all packets."""
        from commands.seed_packet_model import SeedPacket
        from commands import plant_tracking_cli
        from io import StringIO
        import sys

        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir

        for name, latin in [
            ("Avocado", "Persea americana"),
            ("Tomato", "Solanum lycopersicum"),
        ]:
            p = SeedPacket({"variety_name": name, "latin_name": latin})
            fp = self.test_packets_dir / f"{p.data['id']}.md"
            with open(fp, "w") as f:
                f.write(p.to_markdown())

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            plant_tracking_cli.list_seed_packets(type("Args", (), {})())
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        self.assertIn("Avocado", output)
        self.assertIn("Tomato", output)
        self.assertIn("SPKT-", output)

    def test_list_seed_packets_empty(self):
        """Test list-seed-packets handles empty directory."""
        from commands import plant_tracking_cli
        from io import StringIO
        import sys

        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            plant_tracking_cli.list_seed_packets(type("Args", (), {})())
        finally:
            sys.stdout = old_stdout

        self.assertIn("No seed packets", captured.getvalue())

    @mock.patch("sys.exit")
    def test_show_seed_packet_not_found(self, mock_exit):
        """Test show-seed-packet exits for missing packet."""
        from commands import plant_tracking_cli

        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir
        plant_tracking_cli.show_seed_packet(
            type("Args", (), {"packet_id": "SPKT-999"})()
        )
        mock_exit.assert_called_once_with(1)

    def test_show_seed_packet_found(self):
        """Test show-seed-packet displays packet details."""
        from commands.seed_packet_model import SeedPacket
        from commands import plant_tracking_cli
        from io import StringIO
        import sys

        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir

        data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "brand": "Gardners Basics",
        }
        p = SeedPacket(data)
        fp = self.test_packets_dir / f"{p.data['id']}.md"
        with open(fp, "w") as f:
            f.write(p.to_markdown())

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            plant_tracking_cli.show_seed_packet(
                type("Args", (), {"packet_id": p.data["id"]})()
            )
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        self.assertIn("Yellow Habanero", output)
        self.assertIn("Gardners Basics", output)


class TestEndToEnd(unittest.TestCase):
    """Integration tests covering the full seed packet → plant flow."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.test_packets_dir = self.test_db / "seed_packets"
        self.test_packets_dir.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_packet_then_plant_reference(self):
        """Create a seed packet, then create a plant that references it."""
        from commands.seed_packet_model import SeedPacket
        from commands.plant_model import Plant, load_plant_from_file

        # Create seed packet
        packet_data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "brand": "Gardners Basics",
            "days_to_maturity": "80-100",
        }
        packet = SeedPacket(packet_data)
        packet_path = self.test_packets_dir / f"{packet.data['id']}.md"
        with open(packet_path, "w") as f:
            f.write(packet.to_markdown())

        # Create plant referencing the packet
        plant_data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "planting_date": "2026-05-01",
            "seed_packet_id": packet.data["id"],
        }
        plant = Plant(plant_data)
        plant_path = self.test_db / f"{plant.data['id']}.md"
        with open(plant_path, "w") as f:
            f.write(plant.to_markdown())

        # Load and verify
        loaded_plant = load_plant_from_file(plant_path)
        self.assertEqual(loaded_plant.data["seed_packet_id"], packet.data["id"])

        resolved = loaded_plant.get_seed_packet()
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.data["brand"], "Gardners Basics")

    def test_unknown_path_plant_no_packet(self):
        """Test plant with unknown seed packet works correctly."""
        from commands.plant_model import Plant, load_plant_from_file

        plant_data = {
            "variety_name": "Mystery Plant",
            "latin_name": "Unknown unknown",
            "planting_date": "2026-06-01",
            "seed_packet_id": "unknown",
        }
        plant = Plant(plant_data)
        plant_path = self.test_db / f"{plant.data['id']}.md"
        with open(plant_path, "w") as f:
            f.write(plant.to_markdown())

        loaded = load_plant_from_file(plant_path)
        self.assertEqual(loaded.data["seed_packet_id"], "unknown")
        self.assertIsNone(loaded.get_seed_packet())

    def test_packet_fields_not_required_with_seed_packet_id(self):
        """Test that seed packet fields are optional when seed_packet_id is present."""
        from commands.plant_model import Plant

        plant_data = {
            "variety_name": "Yellow Habanero",
            "latin_name": "Capsicum chinense",
            "planting_date": "2026-05-01",
            "seed_packet_id": "SPKT-001",
        }
        # Should not raise - no packet fields needed
        plant = Plant(plant_data)
        self.assertEqual(plant.data["variety_name"], "Yellow Habanero")
        self.assertNotIn("brand", plant.data)

    @mock.patch(
        "builtins.input",
        side_effect=[
            # create_seed_packet: required + 7 optional (empty)
            "Basil",
            "Ocimum basilicum",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            # create_plant: variety, latin, confirm existing packet, date
            "Basil",
            "Ocimum basilicum",
            "Y",
            "2026-07-01",
        ],
    )
    def test_cli_full_flow_packet_then_plant(self, mock_input):
        """Test full CLI flow: create packet, then create plant with that packet."""
        from commands import plant_tracking_cli
        from commands.plant_model import load_plant_from_file

        plant_tracking_cli.DATABASE_DIR = self.test_db
        plant_tracking_cli.PACKETS_DIR = self.test_packets_dir

        # Create packet first
        plant_tracking_cli.create_seed_packet(type("Args", (), {})())

        # Now create plant that matches the packet
        plant_tracking_cli.create_plant(type("Args", (), {})())

        plant_files = list(self.test_db.glob("*.md"))
        self.assertEqual(len(plant_files), 1)

        loaded = load_plant_from_file(plant_files[0])
        self.assertEqual(loaded.data["variety_name"], "Basil")
        self.assertTrue(loaded.data["seed_packet_id"].startswith("SPKT-"))


class TestLabelFormat(unittest.TestCase):
    def test_label_format_creation(self):
        """Test LabelFormat creation and properties"""
        from commands.label_format import LabelFormat

        fmt_40x30 = LabelFormat(
            width_mm=40,
            height_mm=30,
            orientation="landscape",
            name="40x30mm",
            text_column_width=100,
            column_gap=8,
            margin=8,
            latin_name_offset_from_bottom=20,
            qr_code_top_offset=0,
            qr_code_bottom_margin=6,
        )
        self.assertEqual(fmt_40x30.width_mm, 40)
        self.assertEqual(fmt_40x30.height_mm, 30)
        self.assertEqual(fmt_40x30.orientation, "landscape")
        self.assertEqual(fmt_40x30.name, "40x30mm")
        self.assertEqual(fmt_40x30.text_column_width, 100)
        self.assertEqual(fmt_40x30.column_gap, 8)
        self.assertEqual(fmt_40x30.margin, 8)

        # Test pixel calculations
        expected_width_px = int(40 * 203 / 25.4)
        expected_height_px = int(30 * 203 / 25.4)
        self.assertEqual(fmt_40x30.width_px, expected_width_px)
        self.assertEqual(fmt_40x30.height_px, expected_height_px)

    def test_get_label_format(self):
        """Test getting label formats by string"""
        from commands.label_format import get_label_format

        fmt_40x30 = get_label_format("40x30mm")
        self.assertEqual(fmt_40x30.name, "40x30mm")
        self.assertEqual(fmt_40x30.width_mm, 40)
        self.assertEqual(fmt_40x30.height_mm, 30)
        self.assertEqual(fmt_40x30.text_column_width, 100)

        fmt_50x70 = get_label_format("50x70mm")
        self.assertEqual(fmt_50x70.name, "50x70mm")
        self.assertEqual(fmt_50x70.width_mm, 70)
        self.assertEqual(fmt_50x70.height_mm, 50)
        self.assertEqual(fmt_50x70.text_column_width, 120)

        # Test invalid format
        with self.assertRaises(ValueError):
            get_label_format("invalid-format")

    def test_is_format_supported(self):
        """Test format support checking"""
        from commands.label_format import is_format_supported

        self.assertTrue(is_format_supported("40x30mm"))
        self.assertTrue(is_format_supported("50x70mm"))
        self.assertFalse(is_format_supported("invalid-format"))


class TestPrintLabelWithFormat(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        from commands.plant_model import Plant

        self.Plant = Plant

        # Create a test plant
        plant_data = {
            "variety_name": "Test Variety",
            "latin_name": "Testus varietyus",
            "planting_date": "2026-06-01",
        }
        self.test_plant = Plant(plant_data)
        self.test_plant_id = self.test_plant.data["id"]

        plant_file = self.test_db / f"{self.test_plant_id}.md"
        with open(plant_file, "w") as f:
            f.write(self.test_plant.to_markdown())

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @mock.patch("commands.printer._select_printer")
    @mock.patch("commands.printer._find_usb_phomemo_devices")
    def test_print_label_40x30mm_format(self, mock_find_devices, mock_select_printer):
        """Test print_label with 40x30mm format"""
        mock_find_devices.return_value = [
            {
                "model": "M120",
                "bus": 1,
                "address": 1,
                "product_id": 0x5740,
                "serial": "TEST123",
                "description": "Phomemo M120 (bus 001, dev 001) serial=TEST123",
            }
        ]
        mock_select_printer.return_value = mock_find_devices.return_value[0]

        from commands.label_generator import create_label
        from PIL import Image

        # Test label generation with 40x30mm format
        label_path = self.test_dir / "test_40x30_label.png"
        generated_path = create_label(self.test_plant_id, label_path, "40x30mm")

        self.assertTrue(generated_path.exists())

        # Check dimensions
        img = Image.open(generated_path)
        width, height = img.size

        # 40x30mm at 203 DPI should be approximately 320x236 pixels
        expected_width = int(40 * 203 / 25.4)  # 319px
        expected_height = int(30 * 203 / 25.4)  # 239px

        self.assertEqual(width, expected_width)
        self.assertEqual(height, expected_height)

    @mock.patch("commands.printer._select_printer")
    @mock.patch("commands.printer._find_usb_phomemo_devices")
    def test_print_label_50x70mm_format(self, mock_find_devices, mock_select_printer):
        """Test print_label with 50x70mm format"""
        mock_find_devices.return_value = [
            {
                "model": "M120",
                "bus": 1,
                "address": 1,
                "product_id": 0x5740,
                "serial": "TEST123",
                "description": "Phomemo M120 (bus 001, dev 001) serial=TEST123",
            }
        ]
        mock_select_printer.return_value = mock_find_devices.return_value[0]

        from commands.label_generator import create_label
        from PIL import Image

        # Test label generation with 50x70mm format
        label_path = self.test_dir / "test_50x70_label.png"
        generated_path = create_label(self.test_plant_id, label_path, "50x70mm")

        self.assertTrue(generated_path.exists())

        # Check dimensions
        img = Image.open(generated_path)
        width, height = img.size

        # 50x70mm at 203 DPI should be approximately 400x560 pixels
        expected_width = int(50 * 203 / 25.4)  # 399px
        expected_height = int(70 * 203 / 25.4)  # 559px

        self.assertEqual(width, expected_width)
        self.assertEqual(height, expected_height)

    @mock.patch("commands.printer._select_printer")
    @mock.patch("commands.printer._find_usb_phomemo_devices")
    def test_print_label_no_print_flag(self, mock_find_devices, mock_select_printer):
        """Test print_label with --no-print flag"""
        mock_find_devices.return_value = [
            {
                "model": "M120",
                "bus": 1,
                "address": 1,
                "product_id": 0x5740,
                "serial": "TEST123",
                "description": "Phomemo M120 (bus 001, dev 001) serial=TEST123",
            }
        ]
        mock_select_printer.return_value = mock_find_devices.return_value[0]

        from commands.printer import print_label

        # Test that label is generated but not printed when no_print=True
        with mock.patch("commands.printer.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            result = print_label(self.test_plant_id, "40x30mm", no_print=True)

            # Should return True (success)
            self.assertTrue(result)

            # Should not have called lp command for printing
            mock_run.assert_not_called()

    def test_print_label_invalid_format(self):
        """Test print_label with invalid format"""
        from commands.printer import print_label

        result = print_label(self.test_plant_id, "invalid-format")
        self.assertFalse(result)


class TestLabelGenerationFormats(unittest.TestCase):
    """Tests for label generation with different formats."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        from commands.plant_model import Plant

        self.Plant = Plant

        # Create a test plant
        plant_data = {
            "variety_name": "Test Variety",
            "latin_name": "Testus varietyus",
            "planting_date": "2026-06-01",
        }
        plant = self.Plant(plant_data)
        plant_file = self.test_db / f"{plant.data['id']}.md"
        with open(plant_file, "w") as f:
            f.write(plant.to_markdown())
        self.test_plant_id = plant.data["id"]

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_label_dimensions_40x30mm(self):
        """Test that generated label has correct dimensions for 40x30mm format"""
        from commands.label_generator import create_label
        from PIL import Image

        label_path = self.test_dir / "test_label_40x30.png"
        generated_path = create_label(self.test_plant_id, label_path, "40x30mm")

        self.assertTrue(generated_path.exists())

        img = Image.open(generated_path)
        width, height = img.size

        # 40x30mm at 203 DPI
        expected_width = int(40 * 203 / 25.4)
        expected_height = int(30 * 203 / 25.4)

        self.assertEqual(width, expected_width)
        self.assertEqual(height, expected_height)

    def test_label_dimensions_50x70mm(self):
        """Test that generated label has correct dimensions for 50x70mm format"""
        from commands.label_generator import create_label
        from PIL import Image

        label_path = self.test_dir / "test_label_50x70.png"
        generated_path = create_label(self.test_plant_id, label_path, "50x70mm")

        self.assertTrue(generated_path.exists())

        img = Image.open(generated_path)
        width, height = img.size

        # 50x70mm at 203 DPI
        expected_width = int(50 * 203 / 25.4)
        expected_height = int(70 * 203 / 25.4)

        self.assertEqual(width, expected_width)
        self.assertEqual(height, expected_height)

    def test_label_default_format_is_40x30mm(self):
        """Test that default format produces 40x30mm dimensions"""
        from commands.label_generator import create_label
        from PIL import Image

        label_path = self.test_dir / "test_label_default.png"
        generated_path = create_label(self.test_plant_id, label_path)

        self.assertTrue(generated_path.exists())

        img = Image.open(generated_path)
        width, height = img.size

        expected_width = int(40 * 203 / 25.4)
        expected_height = int(30 * 203 / 25.4)

        self.assertEqual(width, expected_width)
        self.assertEqual(height, expected_height)


if __name__ == "__main__":
    unittest.main()


class TestPlantLogModel(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.test_logs_dir = self.test_db / "logs"

        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

        from commands.plant_log_model import (
            PlantLogEntry,
            normalize_water_amount,
            ensure_log_file_exists,
            append_log_entry,
            load_log_entries,
            get_log_file_path,
        )

        self.PlantLogEntry = PlantLogEntry
        self.normalize_water_amount = normalize_water_amount
        self.ensure_log_file_exists = ensure_log_file_exists
        self.append_log_entry = append_log_entry
        self.load_log_entries = load_log_entries
        self.get_log_file_path = get_log_file_path

    def tearDown(self):
        if self.original_db:
            os.environ["PLANT_DATABASE_DIR"] = self.original_db
        else:
            os.environ.pop("PLANT_DATABASE_DIR", None)

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_water_amount_normalization(self):
        """Test water amount normalization to milliliters"""
        test_cases = [
            ("4qt", 3785.412),
            ("1L", 1000),
            ("500ml", 500),
            ("1 cup", 236.588),
            ("2 tbsp", 29.5736),
            ("1 tsp", 4.92892),
            ("8 oz", 236.588),
            ("1 fl oz", 29.5735),
        ]

        import re as re_mod

        for amount_str, expected_ml in test_cases:
            with self.subTest(amount=amount_str):
                result = self.normalize_water_amount(amount_str)
                self.assertAlmostEqual(result["value_ml"], expected_ml, places=4)
                expected_val = float(
                    re_mod.match(r"^\d+(?:\.\d+)?", amount_str).group()
                )
                self.assertEqual(result["display_value"], expected_val)

    def test_water_amount_normalization_invalid(self):
        """Test that invalid water amounts raise ValueError"""
        invalid_amounts = ["invalid", "4 xyz", "100", ""]
        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    self.normalize_water_amount(amount)

    def test_plant_log_entry_creation(self):
        """Test creating valid log entries"""
        humidity_data = {
            "plant_id": "TEST-2026-001",
            "event_type": "humidity",
            "level": 6,
        }
        humidity_entry = self.PlantLogEntry(humidity_data)
        self.assertEqual(humidity_entry.data["plant_id"], "TEST-2026-001")
        self.assertEqual(humidity_entry.data["event_type"], "humidity")
        self.assertEqual(humidity_entry.data["level"], 6)

        water_data = {
            "plant_id": "TEST-2026-001",
            "event_type": "water",
            "amount_ml": 500,
            "amount_display": "500 ml",
        }
        water_entry = self.PlantLogEntry(water_data)
        self.assertEqual(water_entry.data["event_type"], "water")

        fert_data = {
            "plant_id": "TEST-2026-001",
            "event_type": "fertilizer",
            "type": "Tomorite",
            "strength": "1/2",
        }
        fert_entry = self.PlantLogEntry(fert_data)
        self.assertEqual(fert_entry.data["event_type"], "fertilizer")
        self.assertEqual(fert_entry.data["type"], "Tomorite")

        note_data = {
            "plant_id": "TEST-2026-001",
            "event_type": "note",
            "text": "Leaves look yellowish",
        }
        note_entry = self.PlantLogEntry(note_data)
        self.assertEqual(note_entry.data["event_type"], "note")
        self.assertEqual(note_entry.data["text"], "Leaves look yellowish")

    def test_plant_log_entry_validation(self):
        """Test validation of log entries"""
        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({"event_type": "humidity", "level": 5})
        self.assertIn("Missing required field: plant_id", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({"plant_id": "TEST-2026-001", "level": 5})
        self.assertIn("Missing required field: event_type", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry(
                {"plant_id": "TEST-2026-001", "event_type": "invalid", "level": 5}
            )
        self.assertIn("Invalid event_type", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry(
                {"plant_id": "TEST-2026-001", "event_type": "humidity", "level": 15}
            )
        self.assertIn("Humidity level must be between 1 and 10", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry(
                {
                    "plant_id": "TEST-2026-001",
                    "event_type": "humidity",
                    "level": "invalid",
                }
            )
        self.assertIn("Humidity level must be an integer", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({"plant_id": "TEST-2026-001", "event_type": "water"})
        self.assertIn("Missing required field: amount", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry(
                {
                    "plant_id": "TEST-2026-001",
                    "event_type": "fertilizer",
                    "type": "Tomorite",
                }
            )
        self.assertIn("Missing required field: strength", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry(
                {
                    "plant_id": "TEST-2026-001",
                    "event_type": "fertilizer",
                    "strength": "1/2",
                }
            )
        self.assertIn("Missing required field: type", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.PlantLogEntry({"plant_id": "TEST-2026-001", "event_type": "note"})
        self.assertIn("Missing required field: text", str(ctx.exception))

    def test_log_file_creation_and_appending(self):
        """Test that log file is created and entries are appended"""
        log_file = self.get_log_file_path()
        if log_file.exists():
            log_file.unlink()

        entry1_data = {
            "plant_id": "TEST-2026-001",
            "event_type": "humidity",
            "level": 6,
            "date": "2026-05-04",
        }
        entry1 = self.PlantLogEntry(entry1_data)
        self.append_log_entry(entry1)

        self.assertTrue(log_file.exists())
        with open(log_file, "r") as f:
            content = f.read()
        self.assertIn("Plant Activity Log", content)
        self.assertIn("TEST-2026-001", content)
        self.assertIn("humidity", content)
        self.assertIn("2026-05-04", content)

        entry2_data = {
            "plant_id": "TEST-2026-001",
            "event_type": "water",
            "amount_ml": 500,
            "amount_display": "500 ml",
            "date": "2026-05-05",
        }
        entry2 = self.PlantLogEntry(entry2_data)
        self.append_log_entry(entry2)

        with open(log_file, "r") as f:
            content = f.read()
        self.assertEqual(content.count("---"), 3)
        self.assertIn("2026-05-04", content)
        self.assertIn("2026-05-05", content)

    def test_load_log_entries(self):
        """Test loading log entries with filtering"""
        log_file = self.get_log_file_path()
        if log_file.exists():
            log_file.unlink()

        entries_data = [
            {
                "plant_id": "TEST-2026-001",
                "event_type": "humidity",
                "level": 6,
                "date": "2026-05-01",
                "timestamp": "2026-05-01T10:00:00Z",
            },
            {
                "plant_id": "TEST-2026-001",
                "event_type": "water",
                "amount_ml": 500,
                "amount_display": "500 ml",
                "date": "2026-05-02",
                "timestamp": "2026-05-02T10:00:00Z",
            },
            {
                "plant_id": "TEST-2026-001",
                "event_type": "humidity",
                "level": 8,
                "date": "2026-05-03",
                "timestamp": "2026-05-03T10:00:00Z",
            },
            {
                "plant_id": "TEST-2026-002",
                "event_type": "humidity",
                "level": 5,
                "date": "2026-05-03",
                "timestamp": "2026-05-03T11:00:00Z",
            },
        ]

        for entry_data in entries_data:
            entry = self.PlantLogEntry(entry_data)
            entry.data["timestamp"] = entry_data["timestamp"]
            self.append_log_entry(entry)

        entries = self.load_log_entries(plant_id="TEST-2026-001")
        self.assertEqual(len(entries), 3)

        humidity_entries = self.load_log_entries(
            plant_id="TEST-2026-001", event_type="humidity"
        )
        self.assertEqual(len(humidity_entries), 2)

        no_entries = self.load_log_entries(plant_id="NONEXISTENT")
        self.assertEqual(len(no_entries), 0)

        all_entries = self.load_log_entries()
        self.assertEqual(len(all_entries), 4)

        timestamps = [e["timestamp"] for e in entries]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_integration_with_plant_model(self):
        """Test that log entries work with existing plant records"""
        from commands.plant_model import Plant

        plant_data = {
            "variety_name": "Test Plant",
            "latin_name": "Testus plantus",
            "planting_date": "2026-05-01",
        }
        plant = Plant(plant_data)
        plant_id = plant.data["id"]

        from commands.plant_model import get_database_dir

        db_dir = get_database_dir()
        plant_file = db_dir / f"{plant.data['id']}.md"
        with open(plant_file, "w") as f:
            f.write(plant.to_markdown())

        entry_data = {"plant_id": plant_id, "event_type": "humidity", "level": 7}
        entry = self.PlantLogEntry(entry_data)
        self.append_log_entry(entry)

        entries = self.load_log_entries(plant_id=plant_id)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["plant_id"], plant_id)
        self.assertEqual(entries[0]["event_type"], "humidity")
        self.assertEqual(entries[0]["level"], 7)


class TestIsPlantDeadHelper(unittest.TestCase):
    """Tests for the _is_plant_dead CLI helper."""

    def setUp(self):
        from commands.plant_tracking_cli import _is_plant_dead

        self._is_plant_dead = _is_plant_dead

    def test_plant_object_with_is_dead_true(self):
        """Plant object with is_dead=True is dead."""

        class Plant:
            is_dead = True

        self.assertTrue(self._is_plant_dead(Plant()))

    def test_plant_object_with_is_dead_false(self):
        """Plant object with is_dead=False is alive."""

        class Plant:
            is_dead = False

        self.assertFalse(self._is_plant_dead(Plant()))

    def test_dict_based_object_with_death_date(self):
        """Dict-based object with death_date in data is dead."""

        class Record:
            data = {"death_date": "2026-07-01"}

        self.assertTrue(self._is_plant_dead(Record()))

    def test_dict_based_object_without_death_date(self):
        """Dict-based object without death_date in data is alive."""

        class Record:
            data = {"id": "PLANT-2026-001", "variety_name": "Test"}

        self.assertFalse(self._is_plant_dead(Record()))

    def test_neither_is_dead_nor_data(self):
        """Object with neither is_dead nor data is alive."""

        class Bare:
            pass

        self.assertFalse(self._is_plant_dead(Bare()))


class TestListPlantsDBFiltering(unittest.TestCase):
    """Tests that CLI list_plants pushes alive/dead filters to the DB layer."""

    def _make_args(self, alive_only=False, dead_only=False):
        return type("Args", (), {"alive_only": alive_only, "dead_only": dead_only})()

    def _make_domain_plant(self, plant_id, death_date=None):
        p = mock.Mock()
        p.id = plant_id
        p.variety_name = "Test Plant"
        p.latin_name = "Testum testum"
        p.planting_date = date(2026, 5, 1)
        p.is_dead = death_date is not None
        return p

    def _make_file_stub(self, plant_id, death_date=None):
        data = {
            "id": plant_id,
            "variety_name": "Test Plant",
            "latin_name": "Testum testum",
            "planting_date": "2026-05-01",
        }
        if death_date:
            data["death_date"] = death_date

        class Record:
            pass

        record = Record()
        record.data = data
        return record

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_alive_only_passed_to_repository(self, mock_create_uow):
        """alive_only is forwarded to the repository, not filtered in Python."""
        from commands.plant_tracking_cli import list_plants

        uow = mock.Mock()
        uow.plants.list_plants.return_value = iter(
            [self._make_domain_plant("PL-2026-001")]
        )
        mock_create_uow.return_value.__enter__.return_value = uow

        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            list_plants(self._make_args(alive_only=True), db=object())

        uow.plants.list_plants.assert_called_once_with(alive_only=True, dead_only=False)
        self.assertIn("PL-2026-001", mock_stdout.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_dead_only_passed_to_repository(self, mock_create_uow):
        """dead_only is forwarded to the repository, not filtered in Python."""
        from commands.plant_tracking_cli import list_plants

        uow = mock.Mock()
        uow.plants.list_plants.return_value = iter(
            [self._make_domain_plant("PL-2026-002", "2026-07-01")]
        )
        mock_create_uow.return_value.__enter__.return_value = uow

        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            list_plants(self._make_args(dead_only=True), db=object())

        uow.plants.list_plants.assert_called_once_with(alive_only=False, dead_only=True)
        self.assertIn("PL-2026-002", mock_stdout.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_no_filters_passes_falses(self, mock_create_uow):
        """Without flags, the repository is called with both filters False."""
        from commands.plant_tracking_cli import list_plants

        uow = mock.Mock()
        uow.plants.list_plants.return_value = iter([])
        mock_create_uow.return_value.__enter__.return_value = uow

        list_plants(self._make_args(), db=object())

        uow.plants.list_plants.assert_called_once_with(
            alive_only=False, dead_only=False
        )

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_both_flags_rejected_without_db_call(self, mock_create_uow):
        """Specifying both filters is an error and never reaches the DB."""
        from commands.plant_tracking_cli import list_plants

        with self.assertRaises(SystemExit):
            list_plants(self._make_args(alive_only=True, dead_only=True), db=object())

        mock_create_uow.assert_not_called()

    @mock.patch("commands.plant_tracking_cli._get_db", return_value=None)
    @mock.patch("commands.plant_tracking_cli._list_plants_from_files")
    def test_file_fallback_still_filters_in_python(self, mock_list_files, mock_get_db):
        """Markdown fallback path keeps filtering in Python via _is_plant_dead."""
        from commands.plant_tracking_cli import list_plants

        mock_list_files.return_value = [
            self._make_file_stub("PL-2026-001"),
            self._make_file_stub("PL-2026-002", "2026-07-01"),
        ]

        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            list_plants(self._make_args(dead_only=True), db=None)
        output = mock_stdout.getvalue()
        self.assertIn("PL-2026-002", output)
        self.assertNotIn("PL-2026-001", output)

        mock_list_files.return_value = [
            self._make_file_stub("PL-2026-001"),
            self._make_file_stub("PL-2026-002", "2026-07-01"),
        ]
        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            list_plants(self._make_args(alive_only=True), db=None)
        output = mock_stdout.getvalue()
        self.assertIn("PL-2026-001", output)
        self.assertNotIn("PL-2026-002", output)


class TestDatabaseConfigLoading(unittest.TestCase):
    """Regression: .env must be loaded before DATABASE_URL is read."""

    def _restore_database_url(self, original):
        if original is not None:
            os.environ["DATABASE_URL"] = original
        else:
            os.environ.pop("DATABASE_URL", None)

    def test_get_database_url_reads_env_lazily(self):
        """get_database_url reflects the current environment, not an import-time snapshot."""
        from commands import database

        self.addCleanup(setattr, database, "engine", None)
        original = os.environ.get("DATABASE_URL")
        self.addCleanup(self._restore_database_url, original)
        os.environ["DATABASE_URL"] = "postgresql://lazy:test/db"
        self.assertEqual(database.get_database_url(), "postgresql://lazy:test/db")
        os.environ.pop("DATABASE_URL")
        self.assertIsNone(database.get_database_url())

    def test_get_engine_raises_when_url_missing(self):
        """_get_engine raises ValueError when DATABASE_URL is unset."""
        from commands import database

        self.addCleanup(setattr, database, "engine", None)
        database.engine = None
        original = os.environ.get("DATABASE_URL")
        self.addCleanup(self._restore_database_url, original)
        os.environ.pop("DATABASE_URL", None)
        with self.assertRaises(ValueError):
            database._get_engine()

    def test_fresh_interpreter_loads_env_before_database_import(self):
        """A process without DATABASE_URL in its env still resolves it from .env."""
        import subprocess
        import sys

        repo_root = Path(__file__).resolve().parent.parent
        if not (repo_root / ".env").exists():
            self.skipTest("no .env in repo root")

        env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from commands.database import get_database_url; "
                "print(get_database_url() or '')",
            ],
            capture_output=True,
            text=True,
            env=env,
            cwd=repo_root,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("postgresql://"), result.stdout)

    def test_get_db_reports_root_cause_on_failure(self):
        """_get_db surfaces the underlying error instead of failing silently."""
        from commands import plant_tracking_cli as cli

        with mock.patch(
            "commands.database.init_db",
            side_effect=ValueError("DATABASE_URL environment variable must be set"),
        ), mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            db = cli._get_db()

        self.assertIsNone(db)
        self.assertIn(
            "DATABASE_URL environment variable must be set", mock_stderr.getvalue()
        )

    def test_list_plants_warns_on_markdown_fallback(self):
        """list_plants warns on stderr when it falls back to Markdown files."""
        from commands import plant_tracking_cli as cli
        from commands.plant_tracking_cli import list_plants

        args = type("Args", (), {"alive_only": False, "dead_only": False})()
        with mock.patch.object(cli, "_get_db", return_value=None), mock.patch.object(
            cli, "_list_plants_from_files", return_value=[]
        ), mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as mock_stdout, mock.patch(
            "sys.stderr", new_callable=io.StringIO
        ) as mock_stderr:
            list_plants(args)

        self.assertIn("No plants found", mock_stdout.getvalue())
        self.assertIn("Markdown", mock_stderr.getvalue())


class TestPromptDeathDetails(unittest.TestCase):
    """Tests for the _prompt_death_details CLI helper (interactive input loops)."""

    def _call_with_inputs(self, inputs):
        from commands.plant_tracking_cli import _prompt_death_details

        with mock.patch("builtins.input", side_effect=list(inputs)), mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as mock_stdout:
            result = _prompt_death_details()
        return result, mock_stdout.getvalue()

    def test_happy_path_reason_by_number(self):
        """Valid date + numbered reason + comment returns the expected tuple."""
        result, _ = self._call_with_inputs(["2026-07-15", "2", "Fungal infection"])
        self.assertEqual(result, (date(2026, 7, 15), "Disease", "Fungal infection"))

    def test_reason_by_name_case_insensitive(self):
        """A reason name (any case) is accepted without numbering."""
        result, _ = self._call_with_inputs(["2026-07-15", "disease", ""])
        self.assertEqual(result, (date(2026, 7, 15), "Disease", ""))

    def test_future_date_rejected_then_accepted(self):
        """A future date is rejected with a message, then the loop re-prompts."""
        from datetime import timedelta

        future = (date.today() + timedelta(days=1)).isoformat()
        result, output = self._call_with_inputs([future, "2026-07-15", "3", ""])
        self.assertIn("Date cannot be in the future.", output)
        self.assertEqual(result, (date(2026, 7, 15), "Overwatering", ""))

    def test_invalid_date_format_rejected_then_accepted(self):
        """A malformed date is rejected with a message, then the loop re-prompts."""
        result, output = self._call_with_inputs(["07-15-2026", "2026-07-15", "3", ""])
        self.assertIn("Invalid date format", output)
        self.assertEqual(result[0], date(2026, 7, 15))

    def test_invalid_reason_reprompted(self):
        """An out-of-range number and an unknown name both re-prompt."""
        result, output = self._call_with_inputs(
            ["2026-07-15", "99", "not a reason", "2", ""]
        )
        self.assertIn("Please enter a number between 1 and 10", output)
        self.assertIn("Invalid reason", output)
        self.assertEqual(result[1], "Disease")

    def test_other_reason_requires_comment(self):
        """'Other' with an empty comment loops until a non-empty comment is given."""
        # Empty comment is rejected by the loop; the second input is accepted.
        # (input() prompt strings are not emitted when builtins.input is mocked,
        # so behavior is verified via the returned tuple.)
        result, _ = self._call_with_inputs(["2026-07-15", "10", "", "custom cause"])
        self.assertEqual(result, (date(2026, 7, 15), "Other", "custom cause"))


class TestMarkDeadCLI(unittest.TestCase):
    """Tests for the mark_dead CLI command (service-backed path)."""

    PLANT_ID = "PE-2026-001"

    def _make_args(self):
        return type("Args", (), {"plant_id": self.PLANT_ID})()

    def _make_plant(self, is_dead=False, death_date=None):
        plant = mock.Mock()
        plant.id = self.PLANT_ID
        plant.variety_name = "Test Plant"
        plant.latin_name = "Testum testum"
        plant.is_dead = is_dead
        plant.death_date = death_date
        plant.death_reason = "Disease" if is_dead else None
        return plant

    def _make_uow(self, plant, updated=None):
        uow = mock.Mock()
        uow.plants.get_plant.return_value = plant
        uow.plants.update_plant.return_value = updated
        return uow

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_happy_path_marks_plant_dead(self, mock_create_uow):
        """Happy path: prompt results are written via update_plant and reported."""
        from commands import plant_tracking_cli

        plant = self._make_plant()
        updated = mock.Mock()
        updated.death_date = date(2026, 7, 15)
        updated.death_reason = "Disease"
        updated.death_comment = "Fungal infection"
        mock_create_uow.return_value.__enter__.return_value = self._make_uow(
            plant, updated
        )

        with mock.patch(
            "builtins.input",
            side_effect=["2026-07-15", "2", "Fungal infection"],
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            plant_tracking_cli.mark_dead(self._make_args(), db=object())

        uow = mock_create_uow.return_value.__enter__.return_value
        uow.plants.update_plant.assert_called_once_with(
            self.PLANT_ID,
            {
                "death_date": date(2026, 7, 15),
                "death_reason": "Disease",
                "death_comment": "Fungal infection",
            },
        )
        output = mock_stdout.getvalue()
        self.assertIn("marked as dead successfully", output)
        self.assertIn("Disease", output)
        self.assertIn("Fungal infection", output)

    @mock.patch("commands.plant_tracking_cli._get_db", return_value=None)
    def test_service_unavailable_without_db(self, mock_get_db):
        """Without a database, mark_dead exits with a friendly error."""
        from commands import plant_tracking_cli

        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.mark_dead(self._make_args(), db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("requires database service", mock_stdout.getvalue())
        mock_get_db.assert_called_once()

    @mock.patch("commands.plant_tracking_cli._get_db")
    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", False)
    def test_service_unavailable_flag(self, mock_get_db):
        """With the service flag off, mark_dead exits even when db is present."""
        from commands import plant_tracking_cli

        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.mark_dead(self._make_args(), db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("requires database service", mock_stdout.getvalue())
        mock_get_db.assert_not_called()

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_plant_not_found(self, mock_create_uow):
        """A missing plant exits before prompting or writing."""
        from commands import plant_tracking_cli

        mock_create_uow.return_value.__enter__.return_value = self._make_uow(None)

        with mock.patch("builtins.input") as mock_input, mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as mock_stdout:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.mark_dead(self._make_args(), db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant not found", mock_stdout.getvalue())
        mock_input.assert_not_called()
        uow = mock_create_uow.return_value.__enter__.return_value
        uow.plants.update_plant.assert_not_called()

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_already_dead_rejected(self, mock_create_uow):
        """An already-dead plant exits with its existing death details."""
        from commands import plant_tracking_cli

        plant = self._make_plant(is_dead=True, death_date=date(2026, 7, 1))
        mock_create_uow.return_value.__enter__.return_value = self._make_uow(plant)

        with mock.patch("builtins.input") as mock_input, mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as mock_stdout:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.mark_dead(self._make_args(), db=object())

        self.assertEqual(ctx.exception.code, 1)
        output = mock_stdout.getvalue()
        self.assertIn("already marked as dead", output)
        self.assertIn("2026-07-01", output)
        mock_input.assert_not_called()
        uow = mock_create_uow.return_value.__enter__.return_value
        uow.plants.update_plant.assert_not_called()

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_update_returns_none_exits_cleanly(self, mock_create_uow):
        """A None result from update_plant (missing row) exits cleanly, no crash."""
        from commands import plant_tracking_cli

        uow = self._make_uow(self._make_plant())
        uow.plants.update_plant.return_value = None
        mock_create_uow.return_value.__enter__.return_value = uow

        with mock.patch(
            "builtins.input", side_effect=["2026-07-15", "2", ""]
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.mark_dead(self._make_args(), db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant not found", mock_stdout.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_validation_error_from_update(self, mock_create_uow):
        """A ValidationException from the write phase exits with a clean message."""
        from commands import plant_tracking_cli
        from plant_service.domain.exceptions import ValidationException

        uow = self._make_uow(self._make_plant())
        uow.plants.update_plant.side_effect = ValidationException("bad reason")
        mock_create_uow.return_value.__enter__.return_value = uow

        with mock.patch(
            "builtins.input", side_effect=["2026-07-15", "2", ""]
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.mark_dead(self._make_args(), db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Validation error", mock_stdout.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_unexpected_error_from_update(self, mock_create_uow):
        """An unexpected exception from the write phase exits cleanly."""
        from commands import plant_tracking_cli

        uow = self._make_uow(self._make_plant())
        uow.plants.update_plant.side_effect = RuntimeError("boom")
        mock_create_uow.return_value.__enter__.return_value = uow

        with mock.patch(
            "builtins.input", side_effect=["2026-07-15", "2", ""]
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.mark_dead(self._make_args(), db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Unexpected error marking plant as dead", mock_stdout.getvalue())


class TestCLILoggingConfig(unittest.TestCase):
    """Tests for CLI logging configuration in main() per ADR-0009."""

    LOGGER_NAME = "plant_tracking.cli"

    def setUp(self):
        self.logger = logging.getLogger(self.LOGGER_NAME)
        self._saved_handlers = self.logger.handlers
        self._saved_level = self.logger.level
        self.logger.handlers.clear()

    def tearDown(self):
        self.logger.handlers = self._saved_handlers
        self.logger.setLevel(self._saved_level)

    def _run_main(self, env_overrides=None, before_return=None):
        """Run main() with stdout/stderr captured.

        Returns (stdout_text, stderr_text). When env_overrides is None the
        PLANT_TRACKING_LOG_LEVEL variable is removed for the call.
        """
        from commands import plant_tracking_cli

        stdout = io.StringIO()
        stderr = io.StringIO()
        env_patch = (
            mock.patch.dict(os.environ, env_overrides)
            if env_overrides is not None
            else mock.patch.dict(os.environ)
        )
        with env_patch as env, mock.patch("sys.argv", ["plant-tracking"]), mock.patch(
            "sys.stdout", stdout
        ), mock.patch("sys.stderr", stderr):
            if env_overrides is None:
                env.pop("PLANT_TRACKING_LOG_LEVEL", None)
            plant_tracking_cli.main()
            if before_return is not None:
                before_return()
        return stdout.getvalue(), stderr.getvalue()

    def test_unexpected_error_logged_to_stderr_with_format(self):
        """With PLANT_TRACKING_LOG_LEVEL unset, an unexpected exception from
        the CLI logger is written to stderr (not stdout) in the ADR-0009
        format, including the traceback."""

        def log_unexpected():
            try:
                raise RuntimeError("simulated unexpected failure")
            except Exception:
                self.logger.exception("Unexpected error: %s", "simulated failure")

        stdout_text, stderr_text = self._run_main(before_return=log_unexpected)

        self.assertEqual(self.logger.level, logging.INFO)
        matching = [
            line
            for line in stderr_text.splitlines()
            if "Unexpected error: simulated failure" in line
        ]
        self.assertEqual(len(matching), 1)
        self.assertRegex(
            matching[0],
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} "
            r"ERROR plant_tracking\.cli: Unexpected error: simulated failure$",
        )
        self.assertIn("Traceback (most recent call last)", stderr_text)
        self.assertNotIn("simulated failure", stdout_text)

    def test_log_level_from_env_var(self):
        """PLANT_TRACKING_LOG_LEVEL=debug sets the CLI logger to DEBUG."""
        self._run_main(env_overrides={"PLANT_TRACKING_LOG_LEVEL": "debug"})

        self.assertEqual(self.logger.level, logging.DEBUG)

    def test_invalid_log_level_falls_back_to_info(self):
        """An unrecognized PLANT_TRACKING_LOG_LEVEL falls back to INFO."""
        self._run_main(env_overrides={"PLANT_TRACKING_LOG_LEVEL": "bogus"})

        self.assertEqual(self.logger.level, logging.INFO)

    def test_repeated_main_calls_do_not_duplicate_handlers(self):
        """Calling main() multiple times adds at most one stderr handler."""
        for _ in range(2):
            self._run_main()

        self.assertEqual(len(self.logger.handlers), 1)


class TestLogCommandExitCodes(unittest.TestCase):
    """log_* commands must exit 1 on failure paths (ADR-0009)."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

    def tearDown(self):
        os.environ["PLANT_DATABASE_DIR"] = self.original_db
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _make_args(self, **kwargs):
        return type("Args", (), kwargs)()

    def _service_uow(self, plant, entry_side_effect=None):
        uow = mock.Mock()
        uow.plants.get_plant.return_value = plant
        if entry_side_effect is not None:
            uow.logs.create_log_entry.side_effect = entry_side_effect
        return uow

    def test_log_humidity_unknown_plant_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(plant_id="NOPE-1", level=5, date=None)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_humidity(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant ID 'NOPE-1' not found", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_humidity_unexpected_error_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        mock_create_uow.return_value.__enter__.return_value = self._service_uow(
            mock.Mock(), entry_side_effect=RuntimeError("boom")
        )
        args = self._make_args(plant_id="P1", level=5, date=None)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_humidity(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("boom", out.getvalue())

    def test_log_water_unknown_plant_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(plant_id="NOPE-1", amount="1L", date=None)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_water(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant ID 'NOPE-1' not found", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_water_invalid_amount_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        mock_create_uow.return_value.__enter__.return_value = self._service_uow(
            mock.Mock()
        )
        args = self._make_args(plant_id="P1", amount="not-a-volume", date=None)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_water(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Invalid water amount", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_water_unexpected_error_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        mock_create_uow.return_value.__enter__.return_value = self._service_uow(
            mock.Mock(), entry_side_effect=RuntimeError("boom")
        )
        args = self._make_args(plant_id="P1", amount="1L", date=None)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_water(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("boom", out.getvalue())

    def test_log_fertilizer_unknown_plant_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(
            plant_id="NOPE-1", type="compost tea", strength="1/2", date=None
        )
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_fertilizer(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant ID 'NOPE-1' not found", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_fertilizer_unexpected_error_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        mock_create_uow.return_value.__enter__.return_value = self._service_uow(
            mock.Mock(), entry_side_effect=RuntimeError("boom")
        )
        args = self._make_args(plant_id="P1", type="tea", strength="1/2", date=None)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_fertilizer(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("boom", out.getvalue())

    def test_log_note_missing_file_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(
            plant_id="P1",
            text=None,
            file=str(self.test_db / "missing.md"),
            date=None,
        )
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_note(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("File not found", out.getvalue())

    def test_log_note_no_text_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(plant_id="P1", text=None, file=None, date=None)
        with mock.patch("sys.stdin") as mock_stdin, mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as out:
            mock_stdin.isatty.return_value = True
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_note(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("No note text provided", out.getvalue())

    def test_log_note_empty_text_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(plant_id="P1", text="   ", file=None, date=None)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_note(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Note text is empty", out.getvalue())

    def test_log_note_unknown_plant_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(plant_id="NOPE-1", text="hello", file=None, date=None)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_note(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant ID 'NOPE-1' not found", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_note_unexpected_error_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        mock_create_uow.return_value.__enter__.return_value = self._service_uow(
            mock.Mock(), entry_side_effect=RuntimeError("boom")
        )
        args = self._make_args(plant_id="P1", text="hello", file=None, date=None)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_note(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("boom", out.getvalue())

    def test_log_list_unknown_plant_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(plant_id="NOPE-1", type="all")
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.log_list(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant ID 'NOPE-1' not found", out.getvalue())


class TestMediaCommandExitCodes(unittest.TestCase):
    """media_* commands must exit 1 on failure paths (ADR-0009)."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)
        self.image_path = self.test_db / "photo.png"
        self.image_path.write_bytes(b"fake image")

    def tearDown(self):
        os.environ["PLANT_DATABASE_DIR"] = self.original_db
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _make_args(self, **kwargs):
        return type("Args", (), kwargs)()

    def test_media_add_missing_file_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(
            plant_id="P1",
            image_path=str(self.test_db / "nope.png"),
            label=None,
            tags=None,
        )
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_add_attachment(
                    args, db=None, media_type="image"
                )

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("File not found", out.getvalue())

    def test_media_add_unknown_plant_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(
            plant_id="NOPE-1",
            image_path=str(self.image_path),
            label=None,
            tags=None,
        )
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_add_attachment(
                    args, db=None, media_type="image"
                )

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant ID 'NOPE-1' not found", out.getvalue())

    def test_media_add_without_db_service_exits_1(self):
        from commands import plant_tracking_cli

        (self.test_db / "P1.md").write_text("# plant P1\n")
        args = self._make_args(
            plant_id="P1",
            image_path=str(self.image_path),
            label=None,
            tags=None,
        )
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_add_attachment(
                    args, db=None, media_type="image"
                )

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("require database service", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_add_unexpected_error_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        uow = mock.Mock()
        uow.plants.get_plant.return_value = mock.Mock()
        cm = mock.MagicMock()
        cm.__enter__.return_value = uow
        mock_create_uow.side_effect = [cm, RuntimeError("boom")]
        args = self._make_args(
            plant_id="P1",
            image_path=str(self.image_path),
            label=None,
            tags=None,
        )
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_add_attachment(
                    args, db=object(), media_type="image"
                )

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Error creating image attachment: boom", out.getvalue())

    def test_media_list_without_db_service_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(plant_id="P1")
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_list_attachments(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("require database service", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_list_unexpected_error_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        uow = mock.Mock()
        uow.media_attachments.get_media_attachments_by_plant.side_effect = RuntimeError(
            "boom"
        )
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(plant_id="P1")
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_list_attachments(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Error listing media attachments: boom", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_list_empty_result_exits_0(self, mock_create_uow):
        """An empty attachment list is a valid result, not a failure."""
        from commands import plant_tracking_cli

        uow = mock.Mock()
        uow.media_attachments.get_media_attachments_by_plant.return_value = []
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(plant_id="P1")
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            plant_tracking_cli.media_list_attachments(args, db=object())

        self.assertIn("No media attachments found", out.getvalue())

    def test_media_show_without_db_service_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(media_id=1)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_show_attachment(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("require database service", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_show_not_found_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        uow = mock.Mock()
        uow.media_attachments.get_media_attachment.return_value = None
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(media_id=1)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_show_attachment(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Media attachment not found: 1", out.getvalue())

    def test_media_delete_without_db_service_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(media_id=1)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_delete_attachment(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("require database service", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_delete_not_found_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        uow = mock.Mock()
        uow.media_attachments.get_media_attachment.return_value = None
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(media_id=1)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_delete_attachment(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Media attachment not found: 1", out.getvalue())

    @mock.patch("plant_service.service_layer.s3_service.S3Service")
    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_delete_failure_exits_1(self, mock_create_uow, mock_s3):
        from commands import plant_tracking_cli

        uow = mock.Mock()
        uow.media_attachments.get_media_attachment.return_value = mock.Mock()
        uow.media_attachments.delete_media_attachment.return_value = False
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(media_id=1)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_delete_attachment(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Failed to delete media attachment 1", out.getvalue())

    def test_media_url_without_db_service_exits_1(self):
        from commands import plant_tracking_cli

        args = self._make_args(media_id=1)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_get_url(args, db=None)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("require database service", out.getvalue())

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_url_not_found_exits_1(self, mock_create_uow):
        from commands import plant_tracking_cli

        uow = mock.Mock()
        uow.media_attachments.get_media_attachment.return_value = None
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(media_id=1)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_get_url(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Media attachment not found: 1", out.getvalue())

    @mock.patch("plant_service.service_layer.s3_service.S3Service")
    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_url_generation_failure_exits_1(self, mock_create_uow, mock_s3):
        from commands import plant_tracking_cli

        uow = mock.Mock()
        uow.media_attachments.get_media_attachment.return_value = mock.Mock()
        mock_s3.return_value.get_presigned_url.return_value = None
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(media_id=1)
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                plant_tracking_cli.media_get_url(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Failed to generate URL", out.getvalue())


class TestUserCancellationExitCode(unittest.TestCase):
    """User-initiated cancellations must still exit 0 (ADR-0009)."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)

    def tearDown(self):
        os.environ["PLANT_DATABASE_DIR"] = self.original_db
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_create_seed_packet_cancelled_exits_0(self, mock_create_uow):
        """Answering 'n' to 'Create anyway?' returns normally (exit 0)."""
        from commands import plant_tracking_cli

        existing = mock.Mock()
        existing.variety_name = "Yellow Habanero"
        existing.latin_name = "Capsicum chinense"
        existing.id = "SP-2026-001"
        existing.brand = "SeedCo"
        uow = mock.Mock()
        uow.seed_packets.list_seed_packets.return_value = iter([existing])
        mock_create_uow.return_value.__enter__.return_value = uow

        args = type("Args", (), {})()
        with mock.patch(
            "builtins.input",
            side_effect=["Yellow Habanero", "Capsicum chinense", "n"],
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            plant_tracking_cli.create_seed_packet(
                args, db=object(), packets_dir=self.test_db
            )

        self.assertIn("Cancelled.", out.getvalue())


class TestSilentPathWarnings(unittest.TestCase):
    """Formerly-silent except paths must log a warning (ADR-0009 §4).

    Each test covers one representative silent path per command family and
    asserts both that a warning is logged and that the fallback behavior
    still executes.
    """

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)
        from commands import plant_tracking_cli

        self.cli = plant_tracking_cli

    def tearDown(self):
        os.environ["PLANT_DATABASE_DIR"] = self.original_db
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _make_args(self, **kwargs):
        return type("Args", (), kwargs)()

    def _fail_uow(self, mock_create_uow):
        """Make entering the unit-of-work context raise (simulated DB failure)."""
        mock_create_uow.return_value.__enter__.side_effect = RuntimeError("db down")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_humidity_plant_check_failure_warns_and_falls_back(
        self, mock_create_uow
    ):
        self._fail_uow(mock_create_uow)
        args = self._make_args(plant_id="P1", level=5, date=None)
        with mock.patch.object(self.cli.logger, "warning") as mock_warning, mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as out:
            with self.assertRaises(SystemExit) as ctx:
                self.cli.log_humidity(args, db=object())

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant ID 'P1' not found", out.getvalue())
        mock_warning.assert_called_once()
        self.assertEqual(
            mock_warning.call_args[0][0],
            "Plant existence check failed for plant_id=%s",
        )
        self.assertEqual(mock_warning.call_args[0][1], "P1")
        self.assertTrue(mock_warning.call_args.kwargs.get("exc_info"))

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_create_plant_genus_lookup_failure_warns_and_falls_back(
        self, mock_create_uow
    ):
        self._fail_uow(mock_create_uow)
        inputs = iter(
            [
                "Test Variety",
                "Testum testum",  # latin name prompt (fallback)
                "n",  # create genus? no
                "C",  # packet choice: skip
                "",  # brand
                "",  # days to maturity
                "",  # germination
                "",  # depth
                "",  # spacing
                "",  # sun
                "",  # indoor start
                "2026-07-15",  # planting date
            ]
        )
        args = self._make_args()
        with mock.patch.object(self.cli.logger, "warning") as mock_warning, mock.patch(
            "builtins.input", side_effect=lambda _: next(inputs)
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                self.cli.create_plant(
                    args,
                    db=object(),
                    database_dir=self.test_db,
                    packets_dir=self.test_db,
                    genera_dir=self.test_db,
                )

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Error creating plant record", out.getvalue())
        messages = [c[0][0] for c in mock_warning.call_args_list]
        self.assertIn("Genus lookup failed for variety_name=%s", messages)
        variety_args = [
            c[0][1]
            for c in mock_warning.call_args_list
            if c[0][0] == "Genus lookup failed for variety_name=%s"
        ]
        self.assertEqual(variety_args, ["Test Variety"])

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_create_seed_packet_duplicate_check_failure_warns_and_falls_back(
        self, mock_create_uow
    ):
        self._fail_uow(mock_create_uow)
        inputs = iter(
            [
                "Test Variety",
                "Testum testum",
                "",  # 7 optional fields
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )
        args = self._make_args()
        with mock.patch.object(self.cli.logger, "warning") as mock_warning, mock.patch(
            "builtins.input", side_effect=lambda _: next(inputs)
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                self.cli.create_seed_packet(args, db=object(), packets_dir=self.test_db)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Error creating seed packet", out.getvalue())
        mock_warning.assert_called_once()
        self.assertEqual(
            mock_warning.call_args[0][0],
            "Duplicate seed packet check failed for variety_name=%s, latin_name=%s",
        )

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_create_genus_duplicate_check_failure_warns_and_falls_back(
        self, mock_create_uow
    ):
        self._fail_uow(mock_create_uow)
        args = self._make_args()
        with mock.patch.object(self.cli.logger, "warning") as mock_warning, mock.patch(
            "builtins.input", side_effect=["Test Variety", "Testum testum"]
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            with self.assertRaises(SystemExit) as ctx:
                self.cli.create_genus(args, db=object(), genera_dir=self.test_db)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Error creating genus", out.getvalue())
        mock_warning.assert_called_once()
        self.assertEqual(
            mock_warning.call_args[0][0],
            "Duplicate genus check failed for variety_name=%s, latin_name=%s",
        )

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_add_plant_check_failure_warns_and_falls_back(self, mock_create_uow):
        self._fail_uow(mock_create_uow)
        image = self.test_db / "photo.png"
        image.write_bytes(b"fake image")
        args = self._make_args(
            plant_id="P1", image_path=str(image), label=None, tags=None
        )
        with mock.patch.object(self.cli.logger, "warning") as mock_warning, mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as out:
            with self.assertRaises(SystemExit) as ctx:
                self.cli.media_add_attachment(args, db=object(), media_type="image")

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Plant ID 'P1' not found", out.getvalue())
        mock_warning.assert_called_once()
        self.assertEqual(
            mock_warning.call_args[0][0],
            "Plant existence check failed for plant_id=%s",
        )
        self.assertEqual(mock_warning.call_args[0][1], "P1")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_warning_reaches_stderr_via_configured_handler(self, mock_create_uow):
        """End-to-end: the warning flows to stderr through the ADR-0009 handler."""
        self._fail_uow(mock_create_uow)

        logger = logging.getLogger("plant_tracking.cli")
        saved_handlers, saved_level = logger.handlers, logger.level
        logger.handlers.clear()
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            args = self._make_args(plant_id="P1", level=5, date=None)
            with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
                self.cli._configure_logging()
                with self.assertRaises(SystemExit):
                    self.cli.log_humidity(args, db=object())
        finally:
            logger.handlers, logger.level = saved_handlers, saved_level

        self.assertIn("Plant existence check failed for plant_id=P1", stderr.getvalue())
        self.assertNotIn("Plant existence check failed", stdout.getvalue())


class TestUnexpectedErrorLogging(unittest.TestCase):
    """Unexpected errors must log a full traceback to stderr (ADR-0009 §2)
    while the user only sees the concise message on stdout."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db = self.test_dir / "test_database"
        self.test_db.mkdir()
        self.original_db = os.environ.get("PLANT_DATABASE_DIR", "database")
        os.environ["PLANT_DATABASE_DIR"] = str(self.test_db)
        from commands import plant_tracking_cli

        self.cli = plant_tracking_cli
        self._logger = logging.getLogger("plant_tracking.cli")
        self._saved_handlers = self._logger.handlers
        self._saved_level = self._logger.level

    def tearDown(self):
        self._logger.handlers = self._saved_handlers
        self._logger.setLevel(self._saved_level)
        os.environ["PLANT_DATABASE_DIR"] = self.original_db
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _make_args(self, **kwargs):
        return type("Args", (), kwargs)()

    def _run_with_logging(self, fn):
        """Run fn() with the ADR-0009 logging configured on captured streams.

        Returns (stdout_text, stderr_text, exit_code); exit_code is None
        when fn returns normally.
        """
        self._logger.handlers.clear()
        stdout = io.StringIO()
        stderr = io.StringIO()
        exit_code = None
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            self.cli._configure_logging()
            try:
                fn()
            except SystemExit as e:
                exit_code = e.code
        return stdout.getvalue(), stderr.getvalue(), exit_code

    def _assert_error_logged(self, stdout_text, stderr_text, message):
        """The formatted ERROR line and traceback are on stderr only."""
        error_lines = [
            line
            for line in stderr_text.splitlines()
            if line.endswith(message) and "plant_tracking.cli:" in line
        ]
        self.assertEqual(len(error_lines), 1)
        self.assertRegex(
            error_lines[0],
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} "
            r"ERROR plant_tracking\.cli: " + re.escape(message),
        )
        self.assertIn("Traceback (most recent call last)", stderr_text)
        self.assertNotIn("Traceback", stdout_text)

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_mark_dead_check_phase_error_logs_traceback(self, mock_create_uow):
        mock_create_uow.return_value.__enter__.side_effect = RuntimeError("boom")
        args = self._make_args(plant_id="P1")
        with mock.patch("builtins.input") as mock_input:
            out, err, code = self._run_with_logging(
                lambda: self.cli.mark_dead(args, db=object())
            )
        self.assertEqual(code, 1)
        mock_input.assert_not_called()
        self._assert_error_logged(out, err, "Unexpected error: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_mark_dead_write_phase_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        plant = mock.Mock()
        plant.is_dead = False
        uow.plants.get_plant.return_value = plant
        uow.plants.update_plant.side_effect = RuntimeError("boom")
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(plant_id="P1")
        with mock.patch("builtins.input", side_effect=["2026-07-15", "2", ""]):
            out, err, code = self._run_with_logging(
                lambda: self.cli.mark_dead(args, db=object())
            )
        self.assertEqual(code, 1)
        self._assert_error_logged(
            out, err, "Unexpected error marking plant as dead: boom"
        )

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_create_plant_error_logs_traceback(self, mock_create_uow):
        mock_create_uow.return_value.__enter__.side_effect = RuntimeError("boom")
        inputs = iter(
            [
                "Test Variety",
                "Testum testum",
                "n",
                "C",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "2026-07-15",
            ]
        )
        args = self._make_args()
        with mock.patch("builtins.input", side_effect=lambda _: next(inputs)):
            out, err, code = self._run_with_logging(
                lambda: self.cli.create_plant(
                    args,
                    db=object(),
                    database_dir=self.test_db,
                    packets_dir=self.test_db,
                    genera_dir=self.test_db,
                )
            )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error creating plant record: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_create_seed_packet_error_logs_traceback(self, mock_create_uow):
        mock_create_uow.return_value.__enter__.side_effect = RuntimeError("boom")
        inputs = iter(["Test Variety", "Testum testum"] + [""] * 7)
        args = self._make_args()
        with mock.patch("builtins.input", side_effect=lambda _: next(inputs)):
            out, err, code = self._run_with_logging(
                lambda: self.cli.create_seed_packet(
                    args, db=object(), packets_dir=self.test_db
                )
            )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error creating seed packet: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_create_genus_error_logs_traceback(self, mock_create_uow):
        mock_create_uow.return_value.__enter__.side_effect = RuntimeError("boom")
        args = self._make_args()
        with mock.patch(
            "builtins.input", side_effect=["Test Variety", "Testum testum"]
        ):
            out, err, code = self._run_with_logging(
                lambda: self.cli.create_genus(
                    args, db=object(), genera_dir=self.test_db
                )
            )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error creating genus: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_show_seed_packet_error_logs_traceback(self, mock_create_uow):
        mock_create_uow.return_value.__enter__.side_effect = RuntimeError("boom")
        args = self._make_args(packet_id="SP-1")
        out, err, code = self._run_with_logging(
            lambda: self.cli.show_seed_packet(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error showing seed packet: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_show_genus_error_logs_traceback(self, mock_create_uow):
        mock_create_uow.return_value.__enter__.side_effect = RuntimeError("boom")
        args = self._make_args(genus_id="GEN-1")
        out, err, code = self._run_with_logging(
            lambda: self.cli.show_genus(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error showing genus: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_show_plant_error_logs_traceback(self, mock_create_uow):
        mock_create_uow.return_value.__enter__.side_effect = RuntimeError("boom")
        args = self._make_args(plant_id="P1")
        out, err, code = self._run_with_logging(
            lambda: self.cli.show_plant(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error showing plant: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_humidity_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        uow.plants.get_plant.return_value = mock.Mock()
        uow.logs.create_log_entry.side_effect = RuntimeError("boom")
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(plant_id="P1", level=5, date=None)
        out, err, code = self._run_with_logging(
            lambda: self.cli.log_humidity(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_water_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        uow.plants.get_plant.return_value = mock.Mock()
        uow.logs.create_log_entry.side_effect = RuntimeError("boom")
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(plant_id="P1", amount="1L", date=None)
        out, err, code = self._run_with_logging(
            lambda: self.cli.log_water(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_fertilizer_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        uow.plants.get_plant.return_value = mock.Mock()
        uow.logs.create_log_entry.side_effect = RuntimeError("boom")
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(plant_id="P1", type="tea", strength="1/2", date=None)
        out, err, code = self._run_with_logging(
            lambda: self.cli.log_fertilizer(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_log_note_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        uow.plants.get_plant.return_value = mock.Mock()
        uow.logs.create_log_entry.side_effect = RuntimeError("boom")
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(plant_id="P1", text="hello", file=None, date=None)
        out, err, code = self._run_with_logging(
            lambda: self.cli.log_note(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_add_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        uow.plants.get_plant.return_value = mock.Mock()
        cm = mock.MagicMock()
        cm.__enter__.return_value = uow
        mock_create_uow.side_effect = [cm, RuntimeError("boom")]
        image = self.test_db / "photo.png"
        image.write_bytes(b"fake image")
        args = self._make_args(
            plant_id="P1", image_path=str(image), label=None, tags=None
        )
        out, err, code = self._run_with_logging(
            lambda: self.cli.media_add_attachment(args, db=object(), media_type="image")
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error creating image attachment: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_list_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        uow.media_attachments.get_media_attachments_by_plant.side_effect = RuntimeError(
            "boom"
        )
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(plant_id="P1")
        out, err, code = self._run_with_logging(
            lambda: self.cli.media_list_attachments(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error listing media attachments: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_show_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        uow.media_attachments.get_media_attachment.side_effect = RuntimeError("boom")
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(media_id=1)
        out, err, code = self._run_with_logging(
            lambda: self.cli.media_show_attachment(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error showing media attachment: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_delete_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        uow.media_attachments.get_media_attachment.side_effect = RuntimeError("boom")
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(media_id=1)
        out, err, code = self._run_with_logging(
            lambda: self.cli.media_delete_attachment(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error deleting media attachment: boom")

    @mock.patch("commands.plant_tracking_cli.SERVICE_AVAILABLE", True)
    @mock.patch("commands.plant_tracking_cli.create_unit_of_work")
    def test_media_url_error_logs_traceback(self, mock_create_uow):
        uow = mock.Mock()
        uow.media_attachments.get_media_attachment.side_effect = RuntimeError("boom")
        mock_create_uow.return_value.__enter__.return_value = uow
        args = self._make_args(media_id=1)
        out, err, code = self._run_with_logging(
            lambda: self.cli.media_get_url(args, db=object())
        )
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error getting media attachment URL: boom")

    @mock.patch("commands.printer.print_label", side_effect=RuntimeError("boom"))
    def test_print_label_error_logs_traceback(self, mock_printer):
        args = self._make_args(plant_id="P1", format="40x30mm", no_print=True)
        out, err, code = self._run_with_logging(lambda: self.cli.print_label(args))
        self.assertEqual(code, 1)
        self._assert_error_logged(out, err, "Error printing label: boom")
