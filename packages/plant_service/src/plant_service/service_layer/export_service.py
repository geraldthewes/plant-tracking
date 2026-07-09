"""Export service implementing iterator/streaming pattern"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator

from plant_service.domain.exceptions import ExportError
from plant_service.adapters.repository.uow import SqlAlchemyUnitOfWork


class ExportService:
    """Service for exporting data with iterator/streaming pattern"""

    def __init__(self, unit_of_work: SqlAlchemyUnitOfWork):
        self.uow = unit_of_work

    def export_plants_streaming(self, batch_size: int = 100) -> Iterator[Dict[str, Any]]:
        """
        Stream plant records in batches to avoid memory overload.
        Returns iterator that yields plant data one batch at a time.
        """
        try:
            with self.uow as uow:
                for plant in uow.plants.list_plants():
                    yield {
                        "id": plant.id,
                        "variety_name": plant.variety_name,
                        "latin_name": plant.latin_name,
                        "brand": plant.brand,
                        "days_to_maturity": plant.days_to_maturity,
                        "germination_time": plant.germination_time,
                        "planting_depth": plant.planting_depth,
                        "spacing": plant.spacing,
                        "sun_requirements": plant.sun_requirements,
                        "indoor_start_time": plant.indoor_start_time,
                        "planting_date": plant.planting_date,
                        "seed_packet_id": plant.seed_packet_id,
                        "genus_id": plant.genus_id,
                    }
        except Exception as e:
            raise ExportError(f"Failed to export plants: {str(e)}")

    def export_genera_streaming(self, batch_size: int = 100) -> Iterator[Dict[str, Any]]:
        """Stream genus records in batches."""
        try:
            with self.uow as uow:
                for genus in uow.genera.list_genera():
                    yield {
                        "id": genus.id,
                        "variety_name": genus.variety_name,
                        "latin_name": genus.latin_name,
                    }
        except Exception as e:
            raise ExportError(f"Failed to export genera: {str(e)}")

    def export_seed_packets_streaming(
        self, batch_size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        """Stream seed packet records in batches."""
        try:
            with self.uow as uow:
                for sp in uow.seed_packets.list_seed_packets():
                    yield {
                        "id": sp.id,
                        "variety_name": sp.variety_name,
                        "latin_name": sp.latin_name,
                        "brand": sp.brand,
                        "days_to_maturity": sp.days_to_maturity,
                        "germination_time": sp.germination_time,
                        "planting_depth": sp.planting_depth,
                        "spacing": sp.spacing,
                        "sun_requirements": sp.sun_requirements,
                        "indoor_start_time": sp.indoor_start_time,
                    }
        except Exception as e:
            raise ExportError(f"Failed to export seed packets: {str(e)}")

    def export_logs_streaming(
        self,
        plant_id: str | None = None,
        event_type: str | None = None,
        batch_size: int = 100,
    ) -> Iterator[Dict[str, Any]]:
        """Stream log entries in batches."""
        try:
            with self.uow as uow:
                for entry in uow.logs.list_entries(
                    plant_id=plant_id, event_type=event_type
                ):
                    yield {
                        "id": entry.id,
                        "plant_id": entry.plant_id,
                        "event_type": entry.event_type,
                        "timestamp": entry.timestamp,
                        "level": entry.level,
                        "amount_ml": entry.amount_ml,
                        "fertilizer_type": entry.fertilizer_type,
                        "fertilizer_strength": entry.fertilizer_strength,
                        "text": entry.text,
                    }
        except Exception as e:
            raise ExportError(f"Failed to export logs: {str(e)}")

    def export_to_markdown(self, output_dir: str) -> Path:
        """
        Export all data to Markdown files using streaming.
        Returns the path to the export directory.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Path(output_dir) / f"markdown_export_{timestamp}"

            (export_path / "seed_packets").mkdir(parents=True, exist_ok=True)
            (export_path / "genera").mkdir(parents=True, exist_ok=True)
            (export_path / "logs").mkdir(parents=True, exist_ok=True)
            (export_path / "plants").mkdir(parents=True, exist_ok=True)

            # Export seed packets
            for packet_data in self.export_seed_packets_streaming():
                self._write_markdown_file(
                    export_path / "seed_packets" / f"{packet_data['id']}.md",
                    packet_data,
                )

            # Export genera
            for genus_data in self.export_genera_streaming():
                self._write_markdown_file(
                    export_path / "genera" / f"{genus_data['id']}.md",
                    genus_data,
                )

            # Export plants
            for plant_data in self.export_plants_streaming():
                self._write_markdown_file(
                    export_path / "plants" / f"{plant_data['id']}.md",
                    plant_data,
                )

            # Export logs
            for log_data in self.export_logs_streaming():
                self._write_markdown_file(
                    export_path / "logs" / f"{log_data['id']}.md",
                    log_data,
                )

            return export_path

        except Exception as e:
            raise ExportError(f"Failed to export to markdown: {str(e)}")

    @staticmethod
    def _write_markdown_file(filepath: Path, data: dict) -> None:
        """Write a single record as a Markdown file with YAML frontmatter."""
        lines = ["---"]
        for key, value in data.items():
            if value is not None:
                lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")
        filepath.write_text("\n".join(lines))
