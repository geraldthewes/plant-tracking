"""
Test suite for plant tracking system
"""

import os
import shutil
import tempfile
import unittest
from unittest import mock
from datetime import datetime, timezone
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
        import re

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
        from commands.seed_packet_model import SeedPacket, load_from_file

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
        total = len(pixels)

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
            "A",
            "Gardners Basics",
            "80-100",
            "7-21",
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

        packet = SeedPacket(
            {
                "variety_name": "Yellow Habanero",
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
        from commands.seed_packet_model import SeedPacket, load_from_file
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
