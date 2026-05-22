"""Unit tests for domain exceptions"""

from plant_service.domain import (
    PlantTrackingServiceException,
    ValidationException,
    PlantNotFoundException,
    SeedPacketNotFoundException,
    GenusNotFoundException,
    PlantLogNotFoundException,
    DatabaseUnavailableError,
    ExportError,
)


class TestExceptionHierarchy:
    def test_base_exception(self):
        exc = PlantTrackingServiceException("test")
        assert isinstance(exc, Exception)
        assert str(exc) == "test"

    def test_validation_exception(self):
        exc = ValidationException("invalid data")
        assert isinstance(exc, PlantTrackingServiceException)
        assert isinstance(exc, Exception)

    def test_plant_not_found(self):
        exc = PlantNotFoundException("plant-001")
        assert isinstance(exc, PlantTrackingServiceException)

    def test_seed_packet_not_found(self):
        exc = SeedPacketNotFoundException("SPKT-001")
        assert isinstance(exc, PlantTrackingServiceException)

    def test_genus_not_found(self):
        exc = GenusNotFoundException("GENUS-001")
        assert isinstance(exc, PlantTrackingServiceException)

    def test_plant_log_not_found(self):
        exc = PlantLogNotFoundException("log-001")
        assert isinstance(exc, PlantTrackingServiceException)

    def test_database_unavailable(self):
        exc = DatabaseUnavailableError("connection refused")
        assert isinstance(exc, PlantTrackingServiceException)

    def test_export_error(self):
        exc = ExportError("failed to export")
        assert isinstance(exc, PlantTrackingServiceException)
