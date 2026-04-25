"""
Test suite for plant tracking system
"""
import os
import shutil
import tempfile
import unittest
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
            'variety_name': 'Test Plant',
            'latin_name': 'Testus plantus',
            'planned_planting_date': '2026-05-01',
        }
        data.update(overrides)
        return data

    def _full_plant_data(self, variety_name="Test Plant", **overrides):
        """Create plant data with all optional fields."""
        data = {
            'variety_name': variety_name,
            'latin_name': 'Testus plantus',
            'brand': 'Test Brand',
            'days_to_maturity': 60,
            'germination_time': '5-10 days',
            'planting_depth': '0.5 inches',
            'spacing': '12 inches',
            'sun_requirements': 'Partial sun',
            'indoor_start_time': '6 weeks',
            'planned_planting_date': '2026-05-01',
        }
        data.update(overrides)
        return data

    def test_plant_creation_required_fields(self):
        """Test creating a plant with only required fields"""
        plant_data = self._required_plant_data(
            variety_name='Habanero',
            latin_name='Capsicum chinense',
            planned_planting_date='2026-05-01',
        )
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data['variety_name'], 'Habanero')
        self.assertTrue(plant.data['id'].startswith('HA'))

    def test_plant_creation_valid_data(self):
        """Test creating a plant with all data"""
        plant_data = self._full_plant_data(variety_name="Yellow Habanero", brand="Burpee")
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data['variety_name'], 'Yellow Habanero')
        self.assertTrue(plant.data['id'].startswith('YEHA'))
        self.assertEqual(plant.data['brand'], 'Burpee')

    def test_plant_id_generation_format(self):
        """Test that plant IDs follow VARIETY-YYYY-SEQ format"""
        import re
        plant_data = self._required_plant_data(
            variety_name='Habanero',
            latin_name='Capsicum chinense',
            planned_planting_date='2026-05-01',
        )
        plant = self.Plant(plant_data)
        pattern = r'^[A-Z]{2,4}-\d{4}-\d{3}$'
        self.assertRegex(plant.data['id'], pattern)

    def test_plant_id_generation_haby(self):
        """Test ID abbreviation for multi-word variety names"""
        plant_data = self._required_plant_data(
            variety_name='Yellow Habanero',
            latin_name='Capsicum chinense',
            planned_planting_date='2026-05-01',
        )
        plant = self.Plant(plant_data)
        self.assertTrue(plant.data['id'].startswith('YEHA'))

    def test_plant_id_generation_single_word(self):
        """Test ID abbreviation for single-word variety names"""
        plant_data = self._required_plant_data(
            variety_name='Habanero',
            latin_name='Capsicum chinense',
            planned_planting_date='2026-05-01',
        )
        plant = self.Plant(plant_data)
        self.assertTrue(plant.data['id'].startswith('HA'))

    def test_plant_markdown_output(self):
        """Test that plant converts to markdown correctly"""
        plant_data = self._full_plant_data(variety_name="Test Plant")
        plant = self.Plant(plant_data)
        markdown = plant.to_markdown()

        self.assertIn('---', markdown)
        self.assertIn('variety_name: Test Plant', markdown)
        self.assertIn('# Plant Record for Test Plant', markdown)
        self.assertIn(f'*ID: {plant.data["id"]}*', markdown)
        self.assertIn('created_at:', markdown)
        self.assertIn('updated_at:', markdown)

    def test_plant_markdown_required_only(self):
        """Test markdown output with only required fields"""
        plant_data = self._required_plant_data(variety_name="Basic Plant")
        plant = self.Plant(plant_data)
        markdown = plant.to_markdown()

        self.assertIn('---', markdown)
        self.assertIn('variety_name: Basic Plant', markdown)
        self.assertIn(f'*ID: {plant.data["id"]}*', markdown)

    def test_plant_missing_required_field(self):
        """Test that missing required field raises ValueError"""
        with self.assertRaises(ValueError) as ctx:
            self.Plant({})
        self.assertIn('Missing required field', str(ctx.exception))

    def test_plant_days_to_maturity_range(self):
        """Test that days_to_maturity accepts range strings"""
        plant_data = self._required_plant_data(days_to_maturity='60-75')
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data['days_to_maturity'], '60-75')

    def test_plant_days_to_maturity_string(self):
        """Test that days_to_maturity accepts single value strings"""
        plant_data = self._required_plant_data(days_to_maturity='90')
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data['days_to_maturity'], '90')

    def test_plant_invalid_date_format(self):
        """Test that invalid date format raises ValueError"""
        plant_data = self._required_plant_data(planned_planting_date='05-01-2026')
        with self.assertRaises(ValueError):
            self.Plant(plant_data)

    def test_record_only_fields_optional(self):
        """Test that record-only fields are accepted without error"""
        plant_data = self._required_plant_data(
            brand='Test Brand',
            days_to_maturity='90',
        )
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data['brand'], 'Test Brand')
        self.assertEqual(plant.data['days_to_maturity'], '90')

    def test_id_sequencing(self):
        """Test that sequence numbers increment correctly"""
        data1 = self._required_plant_data(variety_name="Test Plant")
        plant1 = self.Plant(data1)
        # Save to database so next plant sees it
        filepath = self.test_db / f"{plant1.data['id']}.md"
        with open(filepath, 'w') as f:
            f.write(plant1.to_markdown())

        data2 = self._required_plant_data(variety_name="Test Plant")
        plant2 = self.Plant(data2)

        seq1 = int(plant1.data['id'].split('-')[2])
        seq2 = int(plant2.data['id'].split('-')[2])
        self.assertEqual(seq2, seq1 + 1)

    def test_load_plant_from_file(self):
        """Test loading a plant record from a markdown file"""
        plant_data = self._full_plant_data(variety_name="Loaded Plant")
        plant = self.Plant(plant_data)
        filepath = self.test_db / f"{plant.data['id']}.md"

        with open(filepath, 'w') as f:
            f.write(plant.to_markdown())

        from commands.plant_model import load_plant_from_file
        loaded = load_plant_from_file(filepath)
        self.assertEqual(loaded.data['variety_name'], 'Loaded Plant')
        self.assertEqual(loaded.data['id'], plant.data['id'])

    def test_load_required_only_from_file(self):
        """Test loading a plant record with only required fields"""
        plant_data = self._required_plant_data(variety_name="Required Plant")
        plant = self.Plant(plant_data)
        filepath = self.test_db / f"{plant.data['id']}.md"

        with open(filepath, 'w') as f:
            f.write(plant.to_markdown())

        from commands.plant_model import load_plant_from_file
        loaded = load_plant_from_file(filepath)
        self.assertEqual(loaded.data['variety_name'], 'Required Plant')
        self.assertEqual(loaded.data['id'], plant.data['id'])

    def test_load_invalid_file(self):
        """Test loading an invalid file raises error"""
        invalid_file = self.test_db / "invalid.md"
        with open(invalid_file, 'w') as f:
            f.write("no frontmatter here")

        from commands.plant_model import load_plant_from_file
        with self.assertRaises(ValueError):
            load_plant_from_file(invalid_file)


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
            'variety_name': 'Test Plant',
            'latin_name': 'Testus plantus',
            'planned_planting_date': '2026-05-01',
            'seed_packet_id': 'SPKT-001',
        }
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data['seed_packet_id'], 'SPKT-001')

        filepath = self.test_db / f"{plant.data['id']}.md"
        with open(filepath, 'w') as f:
            f.write(plant.to_markdown())

        from commands.plant_model import load_plant_from_file
        loaded = load_plant_from_file(filepath)
        self.assertEqual(loaded.data['seed_packet_id'], 'SPKT-001')

    def test_plant_with_unknown_seed_packet_id(self):
        """Test that seed_packet_id of 'unknown' is valid."""
        plant_data = {
            'variety_name': 'Test Plant',
            'latin_name': 'Testus plantus',
            'planned_planting_date': '2026-05-01',
            'seed_packet_id': 'unknown',
        }
        plant = self.Plant(plant_data)
        self.assertEqual(plant.data['seed_packet_id'], 'unknown')
        self.assertIsNone(plant.get_seed_packet())

    def test_get_seed_packet_resolves_reference(self):
        """Test that get_seed_packet resolves to the correct SeedPacket."""
        from commands.seed_packet_model import SeedPacket, load_from_file

        packet_data = {
            'variety_name': 'Yellow Habanero',
            'latin_name': 'Capsicum chinense',
            'brand': 'Gardners Basics',
        }
        packet = SeedPacket(packet_data)
        packet_path = self.test_packets_dir / f"{packet.data['id']}.md"
        with open(packet_path, 'w') as f:
            f.write(packet.to_markdown())

        plant_data = {
            'variety_name': 'Yellow Habanero',
            'latin_name': 'Capsicum chinense',
            'planned_planting_date': '2026-05-01',
            'seed_packet_id': packet.data['id'],
        }
        plant = self.Plant(plant_data)
        resolved = plant.get_seed_packet()
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.data['brand'], 'Gardners Basics')

    def test_get_seed_packet_missing_reference(self):
        """Test that get_seed_packet returns None for missing packet."""
        plant_data = {
            'variety_name': 'Test Plant',
            'latin_name': 'Testus plantus',
            'planned_planting_date': '2026-05-01',
            'seed_packet_id': 'SPKT-999',
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
            'variety_name': 'Test Variety',
            'latin_name': 'Testus varietyus',
            'brand': 'Test Brand',
            'days_to_maturity': 75,
            'germination_time': '7 days',
            'planting_depth': '0.25 inches',
            'spacing': '10 inches',
            'sun_requirements': 'Full sun',
            'indoor_start_time': '4 weeks',
            'planned_planting_date': '2026-06-01',
        }
        plant = self.Plant(plant_data)
        plant_file = self.test_db / f"{plant.data['id']}.md"
        with open(plant_file, 'w') as f:
            f.write(plant.to_markdown())
        self.test_plant_id = plant.data['id']

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

        expected_width = int(40 * 300 / 25.4)  # ~472px
        expected_height = int(30 * 300 / 25.4)  # ~354px

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

        img = Image.open(label_path).convert('RGB')
        pixels = list(img.getdata())

        # Count black pixels in the image (QR code area is on the right side)
        black_count = sum(1 for r, g, b in pixels if r < 100 and g < 100 and b < 100)
        total = len(pixels)

        # Labels are mostly white; check for presence of rendered content
        self.assertGreater(black_count, 100, "Expected rendered QR code and text content")

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

    @unittest.mock.patch("commands.printer._select_printer")
    def test_print_missing_plant(self, mock_select):
        """Test that printing a missing plant returns False"""
        mock_select.return_value = None
        from commands.printer import print_label
        result = print_label("NONEXISTENT-2026-001")
        self.assertFalse(result)

    @unittest.mock.patch("commands.printer._select_printer")
    def test_print_nonexistent_file(self, mock_select):
        """Test that printing a nonexistent file returns False"""
        mock_select.return_value = None
        from commands.printer import print_label
        result = print_label("/tmp/does_not_exist.png")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
