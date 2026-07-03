"""Integration tests for repository adapters using SQLite in-memory database"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from plant_service.adapters.repository.models import Base
from plant_service.adapters.repository import (
    SqlAlchemyUnitOfWork,
)


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


class TestPlantRepository:
    def test_create_plant(self, uow):
        with uow:
            plant = uow.plants.create_plant({
                "variety_name": "Yellow Habanero",
                "latin_name": "Capsicum chinense",
                "planting_date": "2026-03-15",
            })
        assert plant.id.startswith("YEHA-")
        assert plant.variety_name == "Yellow Habanero"

    def test_get_plant(self, uow):
        with uow:
            plant = uow.plants.create_plant({
                "variety_name": "Tomato",
                "latin_name": "Solanum lycopersicum",
                "planting_date": "2026-01-01",
            })
            plant_id = plant.id

        with uow:
            retrieved = uow.plants.get_plant(plant_id)
        assert retrieved is not None
        assert retrieved.id == plant_id

    def test_list_plants(self, uow):
        with uow:
            uow.plants.create_plant({
                "variety_name": "Plant 1",
                "latin_name": "Latin 1",
                "planting_date": "2026-01-01",
            })
            uow.plants.create_plant({
                "variety_name": "Plant 2",
                "latin_name": "Latin 2",
                "planting_date": "2026-01-02",
            })

        with uow:
            plants = list(uow.plants.list_plants())
        assert len(plants) == 2


class TestGenusRepository:
    def test_create_genus(self, uow):
        with uow:
            genus = uow.genera.create_genus({
                "variety_name": "Pepper",
                "latin_name": "Capsicum",
            })
        assert genus.id.startswith("GENUS-")
        assert genus.variety_name == "Pepper"

    def test_find_matching(self, uow):
        with uow:
            uow.genera.create_genus({
                "variety_name": "Pepper",
                "latin_name": "Capsicum",
            })

        with uow:
            found = uow.genera.find_matching("Pepper", "Capsicum")
        assert found is not None
        assert found.variety_name == "Pepper"

    def test_find_by_variety_name(self, uow):
        with uow:
            uow.genera.create_genus({
                "variety_name": "Tomato",
                "latin_name": "Solanum",
            })

        with uow:
            found = uow.genera.find_by_variety_name("tomato")
        assert found is not None


class TestSeedPacketRepository:
    def test_create_seed_packet(self, uow):
        with uow:
            sp = uow.seed_packets.create_seed_packet({
                "variety_name": "Yellow Habanero",
                "latin_name": "Capsicum chinense",
                "brand": "Baker",
            })
        assert sp.id.startswith("SPKT-")
        assert sp.brand == "Baker"

    def test_find_matching(self, uow):
        with uow:
            uow.seed_packets.create_seed_packet({
                "variety_name": "Tomato",
                "latin_name": "Solanum lycopersicum",
            })

        with uow:
            found = uow.seed_packets.find_matching("Tomato", "Solanum lycopersicum")
        assert found is not None


class TestLogRepository:
    def test_create_log_entry(self, uow):
        with uow:
            plant = uow.plants.create_plant({
                "variety_name": "Test Plant",
                "latin_name": "Test Latin",
                "planting_date": "2026-01-01",
            })
            plant_id = plant.id

        with uow:
            entry = uow.logs.create_log_entry({
                "plant_id": plant_id,
                "event_type": "humidity",
                "level": 5,
            })
        assert entry.event_type == "humidity"
        assert entry.level == 5

    def test_list_entries(self, uow):
        with uow:
            plant = uow.plants.create_plant({
                "variety_name": "Test Plant",
                "latin_name": "Test Latin",
                "planting_date": "2026-01-01",
            })
            plant_id = plant.id

        with uow:
            uow.logs.create_log_entry({
                "plant_id": plant_id,
                "event_type": "humidity",
                "level": 5,
            })
            uow.logs.create_log_entry({
                "plant_id": plant_id,
                "event_type": "water",
                "amount_ml": 250,
            })

        with uow:
            entries = list(uow.logs.list_entries(plant_id=plant_id))
        assert len(entries) == 2

    def test_list_entries_filter_by_type(self, uow):
        with uow:
            plant = uow.plants.create_plant({
                "variety_name": "Test Plant",
                "latin_name": "Test Latin",
                "planting_date": "2026-01-01",
            })
            plant_id = plant.id

        with uow:
            uow.logs.create_log_entry({
                "plant_id": plant_id,
                "event_type": "humidity",
                "level": 5,
            })
            uow.logs.create_log_entry({
                "plant_id": plant_id,
                "event_type": "water",
                "amount_ml": 250,
            })

        with uow:
            entries = list(uow.logs.list_entries(event_type="humidity"))
        assert len(entries) == 1
        assert entries[0].event_type == "humidity"


class TestUnitOfWork:
    def test_rollback_on_exception(self, session_factory):
        uow = SqlAlchemyUnitOfWork(session_factory)
        try:
            with uow:
                uow.plants.create_plant({
                    "variety_name": "Test Plant",
                    "latin_name": "Test Latin",
                    "planting_date": "2026-01-01",
                })
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Verify the plant was not committed
        uow2 = SqlAlchemyUnitOfWork(session_factory)
        with uow2:
            plants = list(uow2.plants.list_plants())
        assert len(plants) == 0

    def test_commit_success(self, session_factory):
        uow = SqlAlchemyUnitOfWork(session_factory)
        with uow:
            uow.plants.create_plant({
                "variety_name": "Test Plant",
                "latin_name": "Test Latin",
                "planting_date": "2026-01-01",
            })

        # Verify the plant was committed
        uow2 = SqlAlchemyUnitOfWork(session_factory)
        with uow2:
            plants = list(uow2.plants.list_plants())
        assert len(plants) == 1
