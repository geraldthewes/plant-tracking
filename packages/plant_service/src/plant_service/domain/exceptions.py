"""
Domain-specific exceptions for the plant tracking service
"""


class PlantTrackingServiceException(Exception):
    """Base exception for all service-related errors"""
    pass


class ValidationException(PlantTrackingServiceException):
    """Raised when data validation fails"""
    pass


class PlantNotFoundException(PlantTrackingServiceException):
    """Raised when a plant cannot be found"""
    pass


class SeedPacketNotFoundException(PlantTrackingServiceException):
    """Raised when a seed packet cannot be found"""
    pass


class GenusNotFoundException(PlantTrackingServiceException):
    """Raised when a genus cannot be found"""
    pass


class PlantLogNotFoundException(PlantTrackingServiceException):
    """Raised when a plant log entry cannot be found"""
    pass


class DatabaseUnavailableError(PlantTrackingServiceException):
    """Raised when database operations fail"""
    pass


class ExportError(PlantTrackingServiceException):
    """Raised when export operations fail"""
    pass
