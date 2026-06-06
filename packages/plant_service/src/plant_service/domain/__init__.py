"""Domain layer - pure Python models with no infrastructure dependencies"""
from .plant import Plant
from .genus import Genus
from .seed_packet import SeedPacket
from .plant_log import PlantLogEntry
from .media_attachment import (
    MediaAttachment,
    ImageAttachment,
    VideoAttachment,
    AudioAttachment,
)
from .exceptions import (
    PlantTrackingServiceException,
    ValidationException,
    PlantNotFoundException,
    SeedPacketNotFoundException,
    GenusNotFoundException,
    PlantLogNotFoundException,
    DatabaseUnavailableError,
    ExportError,
)
from .utils import normalize_water_amount

__all__ = [
    "Plant",
    "Genus",
    "SeedPacket",
    "PlantLogEntry",
    "MediaAttachment",
    "ImageAttachment",
    "VideoAttachment",
    "AudioAttachment",
    "normalize_water_amount",
    "PlantTrackingServiceException",
    "ValidationException",
    "PlantNotFoundException",
    "SeedPacketNotFoundException",
    "GenusNotFoundException",
    "PlantLogNotFoundException",
    "DatabaseUnavailableError",
    "ExportError",
]
