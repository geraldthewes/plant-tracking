"""
Label generation for plant tracking system
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from plant_model import load_plant_from_file, get_database_dir

# Label specifications (40x30mm at 300 DPI)
LABEL_WIDTH_MM = 40
LABEL_HEIGHT_MM = 30
DPI = 300
LABEL_WIDTH_PX = int(LABEL_WIDTH_MM * DPI / 25.4)  # 472px
LABEL_HEIGHT_PX = int(LABEL_HEIGHT_MM * DPI / 25.4)  # 354px

# Layout constants
TEXT_AREA_WIDTH_RATIO = 0.4  # 40% for text, 60% for QR code
TEXT_AREA_WIDTH = int(LABEL_WIDTH_PX * TEXT_AREA_WIDTH_RATIO)
MARGIN = int(10 * DPI / 25.4)  # 10mm
BOTTOM_TEXT_HEIGHT = int(15 * DPI / 25.4)  # 15mm for bottom text area


def _get_font():
    """Load fonts with fallback to default."""
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font_large = ImageFont.truetype(bold_path, 24)
        font_medium = ImageFont.truetype(font_path, 18)
        font_small = ImageFont.truetype(font_path, 14)
    except (IOError, OSError):
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    return font_large, font_medium, font_small


def _text_height(font):
    """Get approximate text height for a font."""
    if hasattr(font, 'getbbox'):
        bbox = font.getbbox('Ag')
        return bbox[3] - bbox[1] + 2
    return 20  # fallback estimate


def _text_width(font, text):
    """Get text width for a font."""
    if hasattr(font, 'getlength'):
        return font.getlength(text)
    if hasattr(font, 'getbbox'):
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0]
    return len(text) * 6  # rough fallback


def create_label(plant_id: str, output_path: Path = None) -> Path:
    """
    Create a 40x30mm label for a plant

    Args:
        plant_id: The plant ID to encode in QR code
        output_path: Optional output path, defaults to database/{plant_id}_label.png

    Returns:
        Path to the generated label image
    """
    # Load plant data
    database_dir = get_database_dir()
    plant_file = database_dir / f"{plant_id}.md"

    if not plant_file.exists():
        raise FileNotFoundError(f"Plant record not found: {plant_id}")

    plant = load_plant_from_file(plant_file)

    # Set output path
    if output_path is None:
        output_path = database_dir / f"{plant_id}_label.png"

    # Create label image (white background)
    label_image = Image.new('RGB', (LABEL_WIDTH_PX, LABEL_HEIGHT_PX), 'white')
    draw = ImageDraw.Draw(label_image)

    font_large, font_medium, font_small = _get_font()

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(plant_id)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Calculate QR code size to fit right side
    qr_max_size = LABEL_WIDTH_PX - TEXT_AREA_WIDTH - 2 * MARGIN
    qr_img = qr_img.resize((qr_max_size, qr_max_size))

    # Position QR code on right side, centered vertically
    qr_x = TEXT_AREA_WIDTH + (LABEL_WIDTH_PX - TEXT_AREA_WIDTH - qr_img.size[0]) // 2
    qr_y = (LABEL_HEIGHT_PX - BOTTOM_TEXT_HEIGHT - qr_img.size[1]) // 2
    label_image.paste(qr_img, (qr_x, qr_y))

    # Add text on left side
    text_x = MARGIN
    text_y = MARGIN

    # Variety name (large)
    variety_text = plant.data.get('variety_name', 'Unknown Variety')
    draw.text((text_x, text_y), variety_text, fill='black', font=font_large)
    text_y += _text_height(font_large) + 5

    # Latin name (medium)
    latin_text = plant.data.get('latin_name', '')
    if latin_text:
        draw.text((text_x, text_y), latin_text, fill='black', font=font_medium)
        text_y += _text_height(font_medium) + 5

    # Planting date (small)
    planting_date = plant.data.get('planned_planting_date', '')
    if planting_date:
        date_text = f"Planted: {planting_date}"
        draw.text((text_x, text_y), date_text, fill='black', font=font_small)
        text_y += _text_height(font_small) + 5

    # Add bottom text line
    bottom_y = LABEL_HEIGHT_PX - BOTTOM_TEXT_HEIGHT + MARGIN
    bottom_text = f"{variety_text} \u2022 {planting_date}"
    max_chars = int((TEXT_AREA_WIDTH - 2 * MARGIN) / (_text_width(font_small, 'x') * 0.6))
    if len(bottom_text) > max_chars:
        bottom_text = bottom_text[:max_chars - 3] + "..."
    draw.text((MARGIN, bottom_y), bottom_text, fill='black', font=font_small)

    # Save the label
    label_image.save(output_path, 'PNG', dpi=(DPI, DPI))

    return output_path


def main():
    """Command line interface for label generation"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate plant label')
    parser.add_argument('plant_id', help='Plant ID')
    parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    try:
        output_path = Path(args.output) if args.output else None
        label_path = create_label(args.plant_id, output_path)
        print(f"Label generated: {label_path}")
    except Exception as e:
        print(f"Error generating label: {e}")
        return 1

    return 0


if __name__ == "__main__":
    main()
