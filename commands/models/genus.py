"""
SQLAlchemy model for Genus entity
"""
import re
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .plant import Plant


class Genus(Base, TimestampMixin):
    """Genus model matching existing Markdown-based Genus class"""

    __tablename__ = "genera"

    # Primary key
    id: Mapped[str] = mapped_column(String(10), primary_key=True)

    # Core fields
    variety_name: Mapped[str] = mapped_column(String(100), nullable=False)
    latin_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationship
    plants: Mapped[List["Plant"]] = relationship(
        "Plant", lazy="selectin", back_populates="genus"
    )

    def generate_id(self) -> str:
        """
        Generate genus ID in GENUS-NNN format
        """
        seq = self._find_next_sequence()
        return f"GENUS-{seq:03d}"

    def _find_next_sequence(self) -> int:
        """
        Find next sequence number for genus ID
        """
        from sqlalchemy import select

        from commands.database import get_db

        pattern = "GENUS-%"

        with get_db() as session:
            stmt = select(Genus.id).where(Genus.id.like(pattern))
            results = session.execute(stmt).scalars().all()

            max_seq = 0
            regex_pattern = re.compile(r"GENUS-(\d{3})")

            for genus_id in results:
                match = regex_pattern.match(genus_id)
                if match:
                    seq = int(match.group(1))
                    max_seq = max(max_seq, seq)

            return max_seq + 1

    @classmethod
    def create_from_dict(cls, data: dict) -> "Genus":
        """
        Create Genus instance from dictionary data
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
    def find_matching(cls, variety_name: str, latin_name: str) -> Optional["Genus"]:
        """
        Find existing genus by variety_name and latin_name
        """
        from sqlalchemy import select

        from commands.database import get_db

        with get_db() as session:
            stmt = select(Genus).where(
                Genus.variety_name == variety_name,
                Genus.latin_name == latin_name,
            )
            result = session.execute(stmt).scalar_one_or_none()
            return result

    @classmethod
    def find_by_variety_name(cls, variety_name: str) -> Optional["Genus"]:
        """
        Find existing genus by variety_name only (case-insensitive)
        """
        from sqlalchemy import select

        from commands.database import get_db

        with get_db() as session:
            stmt = select(Genus).where(Genus.variety_name.ilike(variety_name))
            result = session.execute(stmt).scalar_one_or_none()
            return result

    @classmethod
    def list_all(cls) -> List["Genus"]:
        """
        Load all genus records
        """
        from sqlalchemy import select

        from commands.database import get_db

        with get_db() as session:
            stmt = select(Genus).order_by(Genus.id)
            results = session.execute(stmt).scalars().all()
            return list(results)
