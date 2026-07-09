"""Base repository class with common database operations"""
from __future__ import annotations

from typing import Generic, TypeVar, Iterator, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository providing common CRUD operations"""

    def __init__(self, session: Session, model_type: Type[T]):
        self.session = session
        self.model_type = model_type

    def get(self, id: str | int) -> Optional[T]:
        """Get entity by ID"""
        return self.session.get(self.model_type, id)

    def list_all(self) -> Iterator[T]:
        """List all entities (returns iterator for streaming)"""
        stmt = select(self.model_type)
        for obj in self.session.execute(stmt).scalars().yield_per(100):
            yield obj

    def add(self, entity: T) -> T:
        """Add new entity"""
        self.session.add(entity)
        self.session.flush()
        return entity

    def update(self, entity: T) -> T:
        """Update existing entity"""
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, id: str | int) -> bool:
        """Delete entity by ID. Returns True if deleted, False if not found."""
        entity = self.get(id)
        if entity:
            self.session.delete(entity)
            self.session.flush()
            return True
        return False

    def get_all_ids(self) -> list[str]:
        """Get all entity IDs for sequence generation"""
        stmt = select(getattr(self.model_type, "id"))
        results = self.session.execute(stmt).scalars().all()
        return [str(r) for r in results]
