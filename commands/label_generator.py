"""
Label generation for plant tracking system
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from .plant_model import load_plant_from_file, get_database_dir

# Label specifications (40x30mm at 203 DPI - typical printer resolution)
LABEL_WIDTH_MM = 40
LABEL_HEIGHT_MM = 30
DPI = 203
LABEL_WIDTH_PX = int(LABEL_WIDTH_MM * DPI / 25.4)  # 40mm -> 320px
LABEL_HEIGHT_PX = int(LABEL_HEIGHT_MM * DPI / 25.4)  # 30mm -> 236px


def _get_font():
    """Load fonts with fallback to default."""
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font_large = ImageFont.truetype(bold_path, 22)  # Slightly smaller plant name
        font_medium = ImageFont.truetype(font_path, 18)
        font_small = ImageFont.truetype(font_path, 14)
    except (IOError, OSError):
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    return font_large, font_medium, font_small


def _text_size(font, text):
    """Get text width and height."""
    if hasattr(font, 'getlength'):
        width = int(font.getlength(text))
    else:
        width = len(text) * 6  # rough estimate
    
    if hasattr(font, 'getbbox'):
        bbox = font.getbbox('Ag')
        height = bbox[3] - bbox[1]
    else:
        height = 20  # fallback
    
    return width, height


def create_label(plant_id: str, output_path: Path = None) -> Path:
    """
    Create a label for a plant (40x30mm at 203 DPI).

    Layout:
        [Plant Name]      (top-left)
        [ID]         [QR ]
        [Date]       [QR ]
                     [QR ]
                     [QR ]
        [Latin Name] (bottom-left)
    """
    database_dir = get_database_dir()
    plant_file = database_dir / f"{plant_id}.md"

    if not plant_file.exists():
        raise FileNotFoundError(f"Plant record not found: {plant_id}")

    plant = load_plant_from_file(plant_file)

    if output_path is None:
        output_path = database_dir / f"{plant_id}_label.png"

    # Get plant data
    variety_text = plant.data.get('variety_name', 'Unknown Variety')
    planting_date = plant.data.get('planned_planting_date', '')
    latin_text = plant.data.get('latin_name', '')

    # Get fonts
    font_large, font_medium, font_small = _get_font()

    # Create label image
    label_image = Image.new('RGB', (LABEL_WIDTH_PX, LABEL_HEIGHT_PX), 'white')
    draw = ImageDraw.Draw(label_image)

    # Measure text
    name_w, name_h = _text_size(font_large, variety_text)
    id_w, id_h = _text_size(font_small, plant_id)
    date_w, date_h = _text_size(font_small, planting_date) if planting_date else (0, 0)
    latin_w, latin_h = _text_size(font_medium, latin_text) if latin_text else (0, 0)

    # Define explicit regions
    MARGIN = 8
    TEXT_COLUMN_WIDTH = 100  # Fixed width for text column
    COLUMN_GAP = 8
    
    # Vertical positions
    name_y = MARGIN
    id_y = name_y + name_h + 6
    date_y = id_y + id_h + 6 if planting_date else None
    latin_y = LABEL_HEIGHT_PX - MARGIN - 20  # 20px from bottom
    
    # QR code region
    qr_x = MARGIN + TEXT_COLUMN_WIDTH + COLUMN_GAP
    qr_y = id_y  # Start at same level as ID
    qr_width = LABEL_WIDTH_PX - qr_x - MARGIN
    qr_height = latin_y - qr_y - 6  # Space above latin name
    
    # Ensure minimum sizes
    qr_width = max(qr_width, 60)
    qr_height = max(qr_height, 60)

    # Generate QR code to exactly fill the allocated space
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,  # smaller boxes for higher density
        border=2,
    )
    qr.add_data(plant_id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    # Resize to exactly fill the allocated space
    qr_img = qr_img.resize((qr_width, qr_height))

    # Draw text elements
    # Plant name at top
    draw.text((MARGIN, MARGIN), variety_text, fill='black', font=font_large)
    
    # ID
    draw.text((MARGIN, id_y), plant_id, fill='black', font=font_small)
    
    # Date
    if planting_date:
        draw.text((MARGIN, id_y + id_h + 6), planting_date, fill='black', font=font_small)
    
    # Latin name at bottom
    if latin_text:
        draw.text((MARGIN, latin_y), latin_text, fill='black', font=font_medium)

    # Place QR code in its allocated region
    label_image.paste(qr_img, (qr_x, qr_y))

    # Convert to 1-bit black and white for better printer compatibility
    # Use a threshold to get pure black/white
    if label_image.mode != '1':
        label_image = label_image.convert('1')

    # Convert to 1-bit black and white for printer compatibility
    if label_image.mode != '1':
        label_image = label_image.convert('1')
    # Save the label with correct DPI for printing
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