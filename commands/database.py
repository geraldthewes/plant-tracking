"""
Database connection and session management for PostgreSQL integration
"""
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import SingletonThreadPool

# Database URL from environment variable
DATABASE_URL: Optional[str] = os.environ.get("DATABASE_URL")

# Engine and session - created lazily
engine = None
SessionLocal = None


def _get_engine():
    """Get or create the database engine."""
    global engine
    if engine is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable must be set")
        engine = create_engine(
            DATABASE_URL,
            poolclass=SingletonThreadPool,
            pool_pre_ping=True,
            echo=False,
        )
    return engine


def _get_session_factory():
    """Get or create the session factory."""
    global SessionLocal
    if SessionLocal is None:
        eng = _get_engine()
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=eng, expire_on_commit=False
        )
    return SessionLocal


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.
    Yields a Session that is automatically closed after use.
    """
    session_factory = _get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables"""
    from . import models  # noqa: F401
    from .models.base import Base

    eng = _get_engine()
    Base.metadata.create_all(bind=eng)


def export_to_markdown() -> None:
    """Export all data from PostgreSQL back to Markdown files for backup"""
    from datetime import datetime

    from .models import Genus, Plant, PlantLogEntry, SeedPacket

    database_dir = get_database_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = database_dir.parent / f"markdown_export_{timestamp}"
    export_dir.mkdir(exist_ok=True)
    (export_dir / "seed_packets").mkdir(exist_ok=True)
    (export_dir / "genera").mkdir(exist_ok=True)
    (export_dir / "logs").mkdir(exist_ok=True)

    session_factory = _get_session_factory()
    session = session_factory()

    try:
        # Export seed packets
        from .seed_packet_model import SeedPacket as MarkdownSeedPacket

        for packet in session.query(SeedPacket).all():
            packet_data = {
                "id": packet.id,
                "variety_name": packet.variety_name,
                "latin_name": packet.latin_name,
                "brand": packet.brand or "unknown",
                "days_to_maturity": packet.days_to_maturity or "unknown",
                "germination_time": packet.germination_time or "unknown",
                "planting_depth": packet.planting_depth or "unknown",
                "spacing": packet.spacing or "unknown",
                "sun_requirements": packet.sun_requirements or "unknown",
                "indoor_start_time": packet.indoor_start_time or "unknown",
            }
            markdown_packet = MarkdownSeedPacket(packet_data)
            packet_file = export_dir / "seed_packets" / f"{packet.id}.md"
            with open(packet_file, "w") as f:
                f.write(markdown_packet.to_markdown())

        # Export genera
        from .genus_model import Genus as MarkdownGenus

        for genus in session.query(Genus).all():
            genus_data = {
                "id": genus.id,
                "variety_name": genus.variety_name,
                "latin_name": genus.latin_name,
            }
            markdown_genus = MarkdownGenus(genus_data)
            genus_file = export_dir / "genera" / f"{genus.id}.md"
            with open(genus_file, "w") as f:
                f.write(markdown_genus.to_markdown())

        # Export plants
        from .plant_model import Plant as MarkdownPlant

        for plant in session.query(Plant).all():
            plant_data = {
                "id": plant.id,
                "variety_name": plant.variety_name,
                "latin_name": plant.latin_name,
                "brand": plant.brand or "unknown",
                "days_to_maturity": plant.days_to_maturity or "unknown",
                "germination_time": plant.germination_time or "unknown",
                "planting_depth": plant.planting_depth or "unknown",
                "spacing": plant.spacing or "unknown",
                "sun_requirements": plant.sun_requirements or "unknown",
                "indoor_start_time": plant.indoor_start_time or "unknown",
                "planting_date": plant.planting_date,
                "seed_packet_id": plant.seed_packet_id or "unknown",
                "genus_id": plant.genus_id or "unknown",
            }
            markdown_plant = MarkdownPlant(plant_data)
            plant_file = export_dir / f"{plant.id}.md"
            with open(plant_file, "w") as f:
                f.write(markdown_plant.to_markdown())

        # Export log entries
        log_entries = session.query(PlantLogEntry).order_by(PlantLogEntry.timestamp).all()
        log_file = export_dir / "logs" / "plant-activity-log.md"

        with open(log_file, "w") as f:
            f.write("# Plant Activity Log\n\n")
            f.write("*Consolidated log of all plant care activities*\n\n---\n")

        for entry in log_entries:
            entry_data = {
                "plant_id": entry.plant_id,
                "event_type": entry.event_type,
                "timestamp": entry.timestamp,
            }
            if entry.event_type == "humidity":
                entry_data["level"] = entry.level
            elif entry.event_type == "water":
                entry_data["amount_ml"] = entry.amount_ml
            elif entry.event_type == "fertilizer":
                entry_data["type"] = entry.fertilizer_type
                entry_data["strength"] = entry.fertilizer_strength
            elif entry.event_type == "note":
                entry_data["text"] = entry.text

            from .plant_log_model import PlantLogEntry as MarkdownPlantLogEntry

            markdown_entry = MarkdownPlantLogEntry(entry_data)
            yaml_content = yaml.dump(
                markdown_entry.to_yaml_entry(), default_flow_style=False, sort_keys=False
            )
            with open(log_file, "a") as f:
                if f.tell() > 0:
                    f.write("\n")
                f.write(f"---\n{yaml_content}...\n")

    finally:
        session.close()

    print(f"Data exported to {export_dir}")


def get_database_dir() -> Path:
    """Get the database directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database"))
