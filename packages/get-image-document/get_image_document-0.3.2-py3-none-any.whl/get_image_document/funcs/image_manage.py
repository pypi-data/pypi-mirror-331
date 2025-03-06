import os
from docx.shared import Inches
from PIL import Image
import tempfile

def add_image_keeping_ratio(run, img_path, cell_width, cell_height, dpi):
    """Adds an image to a Word document while maintaining aspect ratio within the given cell size."""
    with Image.open(img_path) as img:
        width, height = img.size
        dpi = img.info.get("dpi", (dpi, dpi))  # Assume 300 DPI for better quality
        width_in_inches = width / dpi[0]
        height_in_inches = height / dpi[1]

        # Calculate the scaling ratio
        scale_ratio = min(cell_width / width_in_inches, cell_height / height_in_inches)
        new_width = int(width * scale_ratio)
        new_height = int(height * scale_ratio)

        # Save as PNG (to avoid JPEG compression artifacts)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img.save(temp_file, format="PNG", dpi=dpi)
            temp_file_path = temp_file.name

        # Insert into the document
        run.add_picture(temp_file_path, width=Inches(new_width / dpi[0]), height=Inches(new_height / dpi[1]))

        # Clean up temp file
        os.remove(temp_file_path)
