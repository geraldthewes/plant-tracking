"""
Label format specifications for plant tracking system
"""
from dataclasses import dataclass
from enum import Enum


class LabelFormatEnum(Enum):
    """Supported label formats"""
    FORMAT_40X30MM = "40x30mm"
    FORMAT_50X70MM = "50x70mm"


@dataclass
class LabelFormat:
    """Label format specifications with layout configuration"""
    width_mm: float
    height_mm: float
    orientation: str  # "landscape" or "portrait" relative to roll direction
    name: str

    # Layout configuration properties (eliminates need for format name checks)
    text_column_width: int
    column_gap: int
    margin: int
    latin_name_offset_from_bottom: int
    qr_code_top_offset: int  # Offset from ID text top
    qr_code_bottom_margin: int  # Space above latin name

    @property
    def width_px(self) -> int:
        """Width in pixels at 203 DPI"""
        return int(self.width_mm * 203 / 25.4)

    @property
    def height_px(self) -> int:
        """Height in pixels at 203 DPI"""
        return int(self.height_mm * 203 / 25.4)


# Predefined formats with layout configuration
LABEL_FORMATS = {
    LabelFormatEnum.FORMAT_40X30MM.value: LabelFormat(
        width_mm=40,
        height_mm=30,
        orientation="landscape",  # width > height
        name="40x30mm",
        # Layout configuration for 40x30mm (existing behavior)
        text_column_width=100,
        column_gap=8,
        margin=8,
        latin_name_offset_from_bottom=20,
        qr_code_top_offset=0,  # Start at same level as ID
        qr_code_bottom_margin=6  # Space above latin name
    ),
    LabelFormatEnum.FORMAT_50X70MM.value: LabelFormat(
        width_mm=70,
        height_mm=50,
        orientation="portrait",  # rendered wide, then rotated 90° so text flows along 70mm roll direction
        name="50x70mm",
        # Layout configuration for 50x70mm (adjusted for portrait)
        text_column_width=120,  # Wider text column for the 70mm canvas width
        column_gap=8,
        margin=8,
        latin_name_offset_from_bottom=20,
        qr_code_top_offset=0,   # Start at same level as ID
        qr_code_bottom_margin=20 # More space above latin name for tall label
    )
}


def get_label_format(format_str: str) -> LabelFormat:
    """Get LabelFormat by string identifier"""
    if format_str not in LABEL_FORMATS:
        raise ValueError(f"Unsupported label format: {format_str}. Supported formats: {list(LABEL_FORMATS.keys())}")
    return LABEL_FORMATS[format_str]


def is_format_supported(format_str: str) -> bool:
    """Check if a format string is supported"""
    return format_str in LABEL_FORMATS
