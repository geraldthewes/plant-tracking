"""
SQLAlchemy model for Plant entity
"""
import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .genus import Genus
    from .seed_packet import SeedPacket


class Plant(Base, TimestampMixin):
    """Plant model matching existing Markdown-based Plant class"""

    __tablename__ = "plants"

    # Primary key - preserve application-generated ID format
    id: Mapped[str] = mapped_column(String(20), primary_key=True)

    # Core fields
    variety_name: Mapped[str] = mapped_column(String(100), nullable=False)
    latin_name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    days_to_maturity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    germination_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    planting_depth: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    spacing: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sun_requirements: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    indoor_start_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    planting_date: Mapped[str] = mapped_column(String(10), nullable=False)

    # Foreign keys
    seed_packet_id: Mapped[Optional[str]] = mapped_column(
        String(10), ForeignKey("seed_packets.id"), nullable=True
    )
    genus_id: Mapped[Optional[str]] = mapped_column(
        String(10), ForeignKey("genera.id"), nullable=True
    )

    # Relationships
    seed_packet: Mapped[Optional["SeedPacket"]] = relationship(
        "SeedPacket", lazy="selectin", back_populates="plants"
    )
    genus: Mapped[Optional["Genus"]] = relationship(
        "Genus", lazy="selectin", back_populates="plants"
    )

    def generate_id(self, variety_name: str, planting_date: str) -> str:
        """
        Generate plant ID in VARIETY-YYYY-SEQ format
        Preserves exact logic from commands/plant_model.py:103-149
        """
        words = variety_name.upper().split()
        abbrev = "".join([word[:2] for word in words if word.isalpha()])[:4]
        if not abbrev:
            abbrev = variety_name[:4].upper()

        if planting_date:
            year = datetime.strptime(planting_date, "%Y-%m-%d").year
        else:
            year = datetime.now(timezone.utc).year

        seq = self._find_next_sequence(abbrev, year)

        return f"{abbrev}-{year}-{seq:03d}"

    def _find_next_sequence(self, abbrev: str, year: int) -> int:
        """
        Find next sequence number for given abbreviation and year
        """
        from sqlalchemy import select

        from commands.database import get_db

        pattern = f"{abbrev}-{year}-%"

        with get_db() as session:
            stmt = select(Plant.id).where(Plant.id.like(pattern))
            results = session.execute(stmt).scalars().all()

            max_seq = 0
            regex_pattern = re.compile(rf"{abbrev}-{year}-(\d{{3}})")

            for plant_id in results:
                match = regex_pattern.match(plant_id)
                if match:
                    seq = int(match.group(1))
                    max_seq = max(max_seq, seq)

            return max_seq + 1

    @classmethod
    def create_from_dict(cls, data: dict) -> "Plant":
        """
        Create Plant instance from dictionary data
        Preserves validation logic from commands/plant_model.py:68-84
        """
        required_fields = ["variety_name", "latin_name", "planting_date"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        if "genus_id" in data and data["genus_id"] not in (None, "unknown"):
            if not re.match(r"^GENUS-\d{3}$", data["genus_id"]):
                raise ValueError("genus_id must match GENUS-NNN format or be 'unknown'")

        if "planting_date" in data:
            try:
                datetime.strptime(data["planting_date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError("planting_date must be in YYYY-MM-DD format")

        if "id" not in data:
            instance = cls()
            data["id"] = instance.generate_id(
                data["variety_name"],
                data.get("planting_date", ""),
            )

        return cls(**data)
