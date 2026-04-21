# Phomemo M120 Printer Setup for QR Code Printing

## Summary of Setup

This guide documents the setup of a Phomemo M120 thermal label printer on Ubuntu 24.04 for printing QR codes (and other raster images) using the community-developed `phomemo-tools` CUPS driver.

### Steps Performed

1. **Installed Dependencies**
   - CUPS (`cups`)
   - Python Imaging Library (`python3-pil`)
   - Python USB bindings (`python3-usb`)

2. **Built and Installed phomemo-tools**
   - Cloned the repository: `git clone https://github.com/vivier/phomemo-tools.git`
   - Built the CUPS driver in the `cups` subdirectory: `make`
   - Installed the driver: `sudo make install`
   - Restarted CUPS: `sudo systemctl restart cups`

3. **Configured the Printer**
   - Connected the M120 via USB cable (appeared as `/dev/usb/lp4`)
   - Enabled `FileDevice` in `/etc/cups/cups-files.conf` to allow device URIs like `/dev/usb/lp4`
   - Added the printer to CUPS:
     ```bash
     sudo lpadmin -p M120 -E -v /dev/usb/lp4 -P /usr/share/cups/model/Phomemo/Phomemo-M120.ppd.gz
     ```
   - Verified the printer uses the correct PPD (`Phomemo M120`) and is ready.

4. **Tested Printing**
   - Generated a QR code with `qrencode`
   - Printed the QR code image to the M120 printer
   - Confirmed successful output.

## Usage Instructions

### Generating a QR Code

Install `qrencode` if not already present:
```bash
sudo apt install qrencode
```

Create a QR code PNG image:
```bash
# Basic usage: qrencode -s <scale> -l <error_correction> -o <output_file> "<data>"
qrencode -s 10 -l H -o mylabel.png "https://example.com/my-plan"
```

- `-s 10`: Scale factor (higher = larger QR code). Adjust to fit your label.
- `-l H`: Error correction level (L, M, Q, H). H is highest robustness.
- Replace the quoted string with your desired data (URL, text, etc.).

### Printing to the M120

Determine your label size (width x height in mm). Common sizes for the M120 include 50x30mm, 40x60mm, etc. Use the `media=wXXhYY` option where `XX` is width and `YY` is height.

Example print command:
```bash
lp -d M120 -o media=w50h30 mylabel.png
```

- `-d M120`: Specifies the printer name (as set in CUPS).
- `-o media=w50h30`: Sets label size to 50mm width, 30mm height.
- You can also print multiple copies: `-o copies=2`

### Tips for Best Results

- Use high-contrast black-and-white images. The driver rasterizes images for thermal printing.
- If the QR code is too large/small, adjust the `-s` factor in `qrencode` or regenerate at a different size.
- For continuous label rolls, you may need to add `-o MediaType=Continuous` (check your label type).
- Ensure the printer is loaded with labels and ready (green light).

### Troubleshooting

- **Printer not found**: Verify USB connection with `ls -l /dev/usb/lp*` and `lpinfo -v | grep usb`.
- **Filter errors**: Check CUPS error log: `tail -f /var/log/cups/error_log`.
- **Bluetooth alternative**: If you prefer Bluetooth, pair the printer via your desktop Bluetooth settings, then use:
  ```bash
  sudo lpadmin -p M120-BT -E -v phomemo://<MAC_ADDRESS_WITHOUT_COLONS> -P /usr/share/cups/model/Phomemo/Phomemo-M120.ppd.gz
  ```
  Replace `<MAC_ADDRESS_WITHOUT_COLONS>` with the printer's Bluetooth MAC (e.g., `DC0D309023C7`).

### Maintenance

- The `phomemo-tools` driver is installed system-wide. Updates can be made by pulling the repository and re-running `make install`.
- Keep CUPS running: `sudo systemctl status cups`.

## References

- phomemo-tools GitHub: https://github.com/vivier/phomemo-tools
- CUPS documentation: https://www.cups.org/

--- 

*Setup completed by Gerald on $(date +%Y-%m-%d).*