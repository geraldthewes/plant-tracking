"""Unit tests for domain utilities"""
import pytest

from plant_service.domain import normalize_water_amount


class TestNormalizeWaterAmount:
    def test_milliliters(self):
        result = normalize_water_amount("250 ml")
        assert result["value_ml"] == pytest.approx(250.0)
        assert result["display_value"] == 250.0
        assert result["display_unit"] == "ml"

    def test_liters(self):
        result = normalize_water_amount("1 L")
        assert result["value_ml"] == pytest.approx(1000.0)

    def test_cups(self):
        result = normalize_water_amount("2 cups")
        assert result["value_ml"] == pytest.approx(473.176)

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid water amount format"):
            normalize_water_amount("two cups")

    def test_unsupported_unit(self):
        with pytest.raises(ValueError, match="Unsupported water unit"):
            normalize_water_amount("1 gallon")

    def test_multi_space_unit(self):
        result = normalize_water_amount("5 fluid   ounce")
        assert result["value_ml"] == pytest.approx(147.8675)
        assert result["display_value"] == 5.0
        assert result["display_unit"] == "fluid ounce"
