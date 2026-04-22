"""
Label generation for plant tracking system
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from .plant_model import load_plant_from_file, get_database_dir

# Label specifications (40x30mm at 300 DPI)
LABEL_WIDTH_MM = 40
LABEL_HEIGHT_MM = 30
DPI = 300
LABEL_WIDTH_PX = int(LABEL_WIDTH_MM * DPI / 25.4)  # 472px
LABEL_HEIGHT_PX = int(LABEL_HEIGHT_MM * DPI / 25.4)  # 354px


def _get_font():
    """Load fonts with fallback to default."""
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font_name = ImageFont.truetype(bold_path, 24)
        font_date = ImageFont.truetype(font_path, 14)
        font_latin = ImageFont.truetype(font_path, 18)
    except (IOError, OSError):
        font_name = ImageFont.load_default()
        font_date = ImageFont.load_default()
        font_latin = ImageFont.load_default()
    return font_name, font_date, font_latin


def _size(font, text):
    """Get (width, height) for text with given font."""
    bb = font.getbbox(text)
    ag = font.getbbox('Ag')
    return (bb[2] - bb[0], ag[3] - ag[1] + 2)


def create_label(plant_id: str, output_path: Path = None) -> Path:
    """
    Create a 40x30mm label for a plant.

    Layout:
        [Plant Name (large)]                      │
        [ID]              [ QR CODE ]             │
        [Planted: date]   [ QR CODE ]             │
                          [ QR CODE ]             │
                          [ QR CODE ]             │
        [Latin Name (medium)]                     │
    """
    database_dir = get_database_dir()
    plant_file = database_dir / f"{plant_id}.md"

    if not plant_file.exists():
        raise FileNotFoundError(f"Plant record not found: {plant_id}")

    plant = load_plant_from_file(plant_file)

    if output_path is None:
        output_path = database_dir / f"{plant_id}_label.png"

    variety_text = plant.data.get('variety_name', 'Unknown Variety')
    planting_date = plant.data.get('planned_planting_date', '')
    latin_text = plant.data.get('latin_name', '')

    font_name, font_date, font_latin = _get_font()

    label_image = Image.new('RGB', (LABEL_WIDTH_PX, LABEL_HEIGHT_PX), 'white')
    draw = ImageDraw.Draw(label_image)

    # Measure all text
    name_w, name_h = _size(font_name, variety_text)
    id_w, id_h = _size(font_date, plant_id)
    latin_w, latin_h = _size(font_latin, latin_text) if latin_text else (0, 0)
    date_w, date_h = _size(font_date, f"Planted: {planting_date}") if planting_date else (0, 0)

    # Layout constants
    MARGIN = 8
    ROW_SPACING = 4
    TEXT_START_X = MARGIN

    # Calculate total height needed for text block on left
    text_h = name_h
    if planting_date:
        text_h += id_h + ROW_SPACING + date_h
    else:
        text_h += id_h
    text_h += ROW_SPACING  # bottom padding

    # Position QR code to fill the height of the text block
    qr_top = MARGIN
    qr_bottom = LABEL_HEIGHT_PX - MARGIN - latin_h if latin_text else LABEL_HEIGHT_PX - MARGIN
    qr_height = qr_bottom - qr_top

    # QR code width: use remaining space after left column
    max_left_width = max(name_w, id_w, date_w if planting_date else 0, latin_w)
    left_col_width = max_left_width + 2 * MARGIN
    gap = 8
    qr_width = LABEL_WIDTH_PX - left_col_width - gap - MARGIN
    qr_width = max(qr_width, 50)  # minimum width

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
    qr_img = qr_img.resize((qr_width, qr_height))

    # Draw text on left
    y = MARGIN
    draw.text((TEXT_START_X, y), variety_text, fill='black', font=font_name)
    y += name_h + ROW_SPACING

    draw.text((TEXT_START_X, y), plant_id, fill='black', font=font_date)
    id_y = y

    if planting_date:
        y += id_h + ROW_SPACING
        draw.text((TEXT_START_X, y), f"Planted: {planting_date}", fill='black', font=font_date)
        date_y = y

    # Draw QR code: starts at same vertical position as text block top
    qr_x = left_col_width + gap
    label_image.paste(qr_img, (qr_x, qr_top))

    # Draw latin name at bottom
    if latin_text:
        latin_y = LABEL_HEIGHT_PX - MARGIN - latin_h
        draw.text((TEXT_START_X, latin_y), latin_text, fill='black', font=font_latin)

    # Latin name at bottom-left
    if latin_text:
        draw.text((8, latin_y), latin_text, fill='black', font=font_latin)

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
