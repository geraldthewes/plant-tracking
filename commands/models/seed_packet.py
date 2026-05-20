"""
SQLAlchemy model for SeedPacket entity
"""
import re
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .plant import Plant


class SeedPacket(Base, TimestampMixin):
    """SeedPacket model matching existing Markdown-based SeedPacket class"""

    __tablename__ = "seed_packets"

    # Primary key
    id: Mapped[str] = mapped_column(String(10), primary_key=True)

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

    # Relationship
    plants: Mapped[List["Plant"]] = relationship(
        "Plant", lazy="selectin", back_populates="seed_packet"
    )

    def generate_id(self) -> str:
        """
        Generate seed packet ID in SPKT-NNN format
        """
        seq = self._find_next_sequence()
        return f"SPKT-{seq:03d}"

    def _find_next_sequence(self) -> int:
        """
        Find next sequence number by checking existing seed packet records
        """
        from sqlalchemy import select

        from commands.database import get_db

        pattern = "SPKT-%"

        with get_db() as session:
            stmt = select(SeedPacket.id).where(SeedPacket.id.like(pattern))
            results = session.execute(stmt).scalars().all()

            max_seq = 0
            regex_pattern = re.compile(r"SPKT-(\d{3})")

            for packet_id in results:
                match = regex_pattern.match(packet_id)
                if match:
                    seq = int(match.group(1))
                    max_seq = max(max_seq, seq)

            return max_seq + 1

    @classmethod
    def create_from_dict(cls, data: dict) -> "SeedPacket":
        """
        Create SeedPacket instance from dictionary data
        """
        required_fields = ["variety_name", "latin_name"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")

        if "id" not in data:
            instance = cls()
            data["id"] = instance.generate_id()

        return cls(**data)

    @classmethod
    def find_matching(cls, variety_name: str, latin_name: str) -> Optional["SeedPacket"]:
        """
        Find existing seed packet matching variety_name and latin_name
        """
        from sqlalchemy import select

        from commands.database import get_db

        with get_db() as session:
            stmt = select(SeedPacket).where(
                SeedPacket.variety_name == variety_name,
                SeedPacket.latin_name == latin_name,
            )
            result = session.execute(stmt).scalar_one_or_none()
            return result

    @classmethod
    def list_all(cls) -> List["SeedPacket"]:
        """
        Return all seed packets
        """
        from sqlalchemy import select

        from commands.database import get_db

        with get_db() as session:
            stmt = select(SeedPacket).order_by(SeedPacket.id)
            results = session.execute(stmt).scalars().all()
            return list(results)
