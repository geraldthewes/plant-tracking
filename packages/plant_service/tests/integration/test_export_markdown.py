"""Integration tests for ExportService.export_to_markdown date handling"""
from datetime import date

import pytest
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from plant_service.adapters.repository.models import Base
from plant_service.adapters.repository import (
    SqlAlchemyUnitOfWork,
)
from plant_service.service_layer.export_service import ExportService


@pytest.fixture(scope="function")
def session_factory():
    """Create an in-memory SQLite session factory for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )
    return factory


@pytest.fixture(scope="function")
def uow(session_factory):
    """Create a Unit of Work instance for testing"""
    return SqlAlchemyUnitOfWork(session_factory)


def _parse_frontmatter(content: str) -> dict:
    """Extract and parse YAML frontmatter from written markdown content."""
    assert content.startswith("---\n")
    end = content.rindex("---\n")
    return yaml.safe_load(content[4:end])


class TestExportPlantsMarkdownDates:
    def test_planting_date_exported_as_iso_string(self, uow, tmp_path):
        with uow:
            uow.plants.create_plant({
                "variety_name": "Yellow Habanero",
                "latin_name": "Capsicum chinense",
                "planting_date": date(2026, 3, 15),
            })

        export_dir = ExportService(uow).export_to_markdown(str(tmp_path))

        plant_files = list((export_dir / "plants").glob("*.md"))
        assert len(plant_files) == 1
        parsed = _parse_frontmatter(plant_files[0].read_text())
        assert isinstance(parsed["planting_date"], str)
        assert parsed["planting_date"] == "2026-03-15"
