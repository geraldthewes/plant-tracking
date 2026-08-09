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


@pytest.fixture
def sample_plant_dict():
    """Default plant creation dict for test setup"""
    return {
        "variety_name": "Test Plant",
        "latin_name": "Test Latin",
        "planting_date": "2026-01-01",
    }


@pytest.fixture
def sample_plant(uow, sample_plant_dict):
    """Create and return a committed plant for testing"""
    with uow:
        plant = uow.plants.create_plant(sample_plant_dict)
    return plant


@pytest.fixture
def alive_and_dead_plants(uow, sample_plant_dict):
    """Create an alive plant and a dead plant, return their IDs"""
    with uow:
        alive = uow.plants.create_plant({
            **sample_plant_dict,
            "variety_name": "Alive Plant",
            "latin_name": "Alive Latin",
        })
        dead = uow.plants.create_plant({
            **sample_plant_dict,
            "variety_name": "Dead Plant",
            "latin_name": "Dead Latin",
        })
    with uow:
        uow.plants.update_plant(dead.id, {
            "death_date": "2026-08-01",
            "death_reason": "Drought",
        })
    return alive.id, dead.id


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
        # First, create a plant to get a valid plant_id
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


class TestPlantDeathFields:
    def test_update_plant_death_fields(self, uow, sample_plant):
        assert sample_plant.is_dead is False

        with uow:
            updated = uow.plants.update_plant(sample_plant.id, {
                "death_date": "2026-08-07",
                "death_reason": "Disease",
                "death_comment": "Fungal infection",
            })

        assert updated is not None
        assert updated.death_date == "2026-08-07"
        assert updated.death_reason == "Disease"
        assert updated.death_comment == "Fungal infection"
        assert updated.is_dead is True

    def test_retrieve_dead_plant(self, uow, sample_plant_dict):
        with uow:
            plant = uow.plants.create_plant({
                **sample_plant_dict,
                "variety_name": "Dead Plant",
                "latin_name": "Dead Latin",
            })
            plant_id = plant.id

        with uow:
            uow.plants.update_plant(plant_id, {
                "death_date": "2026-08-01",
                "death_reason": "Drought",
            })

        with uow:
            retrieved = uow.plants.get_plant(plant_id)

        assert retrieved is not None
        assert retrieved.is_dead is True
        assert retrieved.death_date == "2026-08-01"
        assert retrieved.death_reason == "Drought"

    def test_list_plants_includes_death_fields(self, uow, alive_and_dead_plants):
        with uow:
            plants = list(uow.plants.list_plants())

        assert len(plants) == 2
        alive_plants = [p for p in plants if not p.is_dead]
        dead_plants = [p for p in plants if p.is_dead]
        assert len(alive_plants) == 1
        assert len(dead_plants) == 1
        assert dead_plants[0].death_date == "2026-08-01"

    def test_list_plants_identifies_alive(self, uow, alive_and_dead_plants):
        with uow:
            plants = list(uow.plants.list_plants())
            alive_only = [p for p in plants if not p.is_dead]

        assert len(alive_only) == 1
        assert alive_only[0].variety_name == "Alive Plant"

    def test_list_plants_identifies_dead(self, uow, alive_and_dead_plants):
        with uow:
            plants = list(uow.plants.list_plants())
            dead_only = [p for p in plants if p.is_dead]

        assert len(dead_only) == 1
        assert dead_only[0].variety_name == "Dead Plant"

    def test_clear_death_fields(self, uow, sample_plant):
        with uow:
            uow.plants.update_plant(sample_plant.id, {
                "death_date": "2026-08-01",
                "death_reason": "Disease",
            })

        with uow:
            cleared = uow.plants.update_plant(sample_plant.id, {
                "death_date": None,
                "death_reason": None,
                "death_comment": None,
            })

        assert cleared is not None
        assert cleared.is_dead is False
        assert cleared.death_date is None
        assert cleared.death_reason is None
        assert cleared.death_comment is None

    def test_list_plants_alive_only_filter(self, uow, alive_and_dead_plants):
        with uow:
            plants = list(uow.plants.list_plants(alive_only=True))

        assert len(plants) == 1
        assert plants[0].variety_name == "Alive Plant"
        assert plants[0].is_dead is False

    def test_list_plants_dead_only_filter(self, uow, alive_and_dead_plants):
        with uow:
            plants = list(uow.plants.list_plants(dead_only=True))

        assert len(plants) == 1
        assert plants[0].variety_name == "Dead Plant"
        assert plants[0].is_dead is True

    def test_list_plants_no_filter_returns_all(self, uow, alive_and_dead_plants):
        with uow:
            plants = list(uow.plants.list_plants())

        assert len(plants) == 2

    def test_list_plants_both_filters_raises(self, uow, alive_and_dead_plants):
        with uow:
            with pytest.raises(ValueError, match="Cannot specify both alive_only and dead_only"):
                list(uow.plants.list_plants(alive_only=True, dead_only=True))

    def test_list_plants_alive_only_all_dead_db(self, uow, sample_plant_dict):
        with uow:
            plant1 = uow.plants.create_plant({
                **sample_plant_dict,
                "variety_name": "Dead One",
                "latin_name": "Dead Latin",
            })
            plant2 = uow.plants.create_plant({
                **sample_plant_dict,
                "variety_name": "Dead Two",
                "latin_name": "Dead Latin 2",
            })

        with uow:
            uow.plants.update_plant(plant1.id, {
                "death_date": "2026-08-01",
                "death_reason": "Drought",
            })
            uow.plants.update_plant(plant2.id, {
                "death_date": "2026-08-02",
                "death_reason": "Pest infestation",
            })

        with uow:
            plants = list(uow.plants.list_plants(alive_only=True))

        assert len(plants) == 0

    def test_list_plants_dead_only_all_alive_db(self, uow, sample_plant_dict):
        with uow:
            uow.plants.create_plant({
                **sample_plant_dict,
                "variety_name": "Alive One",
                "latin_name": "Alive Latin",
            })
            uow.plants.create_plant({
                **sample_plant_dict,
                "variety_name": "Alive Two",
                "latin_name": "Alive Latin 2",
            })

        with uow:
            plants = list(uow.plants.list_plants(dead_only=True))

        assert len(plants) == 0

    def test_list_plants_empty_db(self, uow):
        with uow:
            plants = list(uow.plants.list_plants())

        assert len(plants) == 0
