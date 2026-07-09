"""Domain utilities - pure functions with no infrastructure dependencies"""
from __future__ import annotations

import re


def normalize_water_amount(amount_str: str) -> dict[str, float | str]:
    """
    Normalize water amount string to standard format.
    Returns dict with 'value_ml' (float in ml), 'display_value', and 'display_unit'.
    Supports: ml, L, qt, cups, tsp, tbsp, oz, fl oz
    """
    match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([a-zA-Z\s]+)\s*$", amount_str.strip())
    if not match:
        raise ValueError(f"Invalid water amount format: {amount_str}")

    value = float(match.group(1))
    display_unit = ' '.join(match.group(2).strip().split())
    unit = display_unit.lower()

    unit_conversion = {
        "ml": 1,
        "milliliter": 1,
        "milliliters": 1,
        "l": 1000,
        "liter": 1000,
        "liters": 1000,
        "qt": 946.353,
        "quart": 946.353,
        "quarts": 946.353,
        "cup": 236.588,
        "cups": 236.588,
        "tsp": 4.92892,
        "teaspoon": 4.92892,
        "teaspoons": 4.92892,
        "tbsp": 14.7868,
        "tablespoon": 14.7868,
        "tablespoons": 14.7868,
        "oz": 29.5735,
        "fluid ounce": 29.5735,
        "fluid ounces": 29.5735,
        "fl oz": 29.5735,
    }

    if unit not in unit_conversion:
        raise ValueError(
            f"Unsupported water unit: {unit}. "
            f"Supported units: ml, L, qt, cups, tsp, tbsp, oz, fl oz"
        )

    value_ml = value * unit_conversion[unit]

    return {"value_ml": value_ml, "display_value": value, "display_unit": display_unit}
