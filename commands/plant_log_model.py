"""
Activity log data model and storage
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

LOG_FILE_NAME = "plant-activity-log.md"


def get_logs_dir() -> Path:
    """Get the logs directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database")) / "logs"


def get_log_file_path() -> Path:
    """Get the full path to the activity log file."""
    return get_logs_dir() / LOG_FILE_NAME


class PlantLogEntry:
    """Represents a single activity log entry"""

    VALID_EVENT_TYPES = {"humidity", "water", "fertilizer", "note"}

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate()
        if "timestamp" not in self.data:
            self.data["timestamp"] = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

    def validate(self):
        """Validate log entry data"""
        required_fields = ["plant_id", "event_type"]
        for field in required_fields:
            if field not in self.data:
                raise ValueError(f"Missing required field: {field}")

        if self.data["event_type"] not in self.VALID_EVENT_TYPES:
            raise ValueError(
                f"Invalid event_type: {self.data['event_type']}. "
                f"Must be one of {self.VALID_EVENT_TYPES}"
            )

        if not isinstance(self.data["plant_id"], str) or not self.data["plant_id"]:
            raise ValueError("plant_id must be a non-empty string")

        if "timestamp" in self.data and self.data["timestamp"]:
            try:
                datetime.strptime(self.data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                raise ValueError("timestamp must be in YYYY-MM-DDTHH:MM:SSZ format")

        event_type = self.data["event_type"]
        if event_type == "humidity":
            if "level" not in self.data:
                raise ValueError("Missing required field: level for humidity event")
            level = self.data["level"]
            if not isinstance(level, int):
                raise ValueError("Humidity level must be an integer between 1 and 10")
            if level < 1 or level > 10:
                raise ValueError("Humidity level must be between 1 and 10")

        elif event_type == "water":
            if "amount_ml" not in self.data and "amount" not in self.data:
                raise ValueError("Missing required field: amount for water event")

        elif event_type == "fertilizer":
            if "type" not in self.data:
                raise ValueError("Missing required field: type for fertilizer event")
            if "strength" not in self.data:
                raise ValueError(
                    "Missing required field: strength for fertilizer event"
                )

        elif event_type == "note":
            if "text" not in self.data:
                raise ValueError("Missing required field: text for note event")

    def to_yaml_entry(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for YAML storage"""
        return self.data.copy()


def normalize_water_amount(amount_str: str) -> Dict[str, Any]:
    """
    Normalize water amount string to standard format.
    Returns dict with 'value_ml' (float in ml), 'display_value', and 'display_unit'.
    Supports: ml, L, qt, cups, tsp, tbsp, oz, fl oz
    """
    match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([a-zA-Z\s]+)\s*$", amount_str.strip())
    if not match:
        raise ValueError(f"Invalid water amount format: {amount_str}")

    value = float(match.group(1))
    unit = match.group(2).strip().lower()

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

    return {"value_ml": value_ml, "display_value": value, "display_unit": unit}


def ensure_log_file_exists():
    """Ensure the log file and directory exist"""
    logs_dir = get_logs_dir()
    logs_dir.mkdir(exist_ok=True)

    log_file = get_log_file_path()
    if not log_file.exists():
        with open(log_file, "w") as f:
            f.write(
                "# Plant Activity Log\n\n"
                "*Consolidated log of all plant care activities*\n\n---\n"
            )


def append_log_entry(entry: PlantLogEntry) -> None:
    """Append a log entry to the consolidated log file"""
    ensure_log_file_exists()

    log_file = get_log_file_path()

    if log_file.exists():
        with open(log_file, "r") as f:
            content = f.read()
    else:
        content = ""

    entry_data = entry.to_yaml_entry()
    yaml_content = yaml.dump(entry_data, default_flow_style=False, sort_keys=False)

    with open(log_file, "a") as f:
        if content and not content.endswith("\n"):
            f.write("\n")
        f.write(f"---\n{yaml_content}...\n")


def load_log_entries(
    plant_id: Optional[str] = None, event_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Load log entries from the consolidated log file.
    Optionally filter by plant_id and/or event_type.
    """
    log_file = get_log_file_path()
    if not log_file.exists():
        return []

    with open(log_file, "r") as f:
        content = f.read()

    if not content.strip():
        return []

    entries = []
    parts = content.split("---\n")

    for part in parts[1:]:
        if not part.strip():
            continue

        if "...\n" in part:
            yaml_str = part.split("...\n")[0]
        else:
            yaml_str = part

        try:
            entry_data = yaml.safe_load(yaml_str)
            if entry_data:
                if plant_id and entry_data.get("plant_id") != plant_id:
                    continue
                if event_type and entry_data.get("event_type") != event_type:
                    continue
                entries.append(entry_data)
        except yaml.YAMLError:
            continue

    entries.sort(key=lambda x: x.get("timestamp", ""))
    return entries


def delete_log_file() -> None:
    """Delete the log file (for testing)"""
    log_file = get_log_file_path()
    if log_file.exists():
        log_file.unlink()
