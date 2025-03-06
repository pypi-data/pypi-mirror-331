import os
from docx.shared import Inches
from PIL import Image
import tempfile


def add_image_keeping_ratio(run, img_path, cell_width, cell_height):
    """Adds an image to a Word document while maintaining aspect ratio within the given cell size."""
    with Image.open(img_path) as img:
        width, height = img.size
        dpi = img.info.get("dpi", (72, 72))  # Default to 72 DPI if missing
        width_in_inches = width / dpi[0]
        height_in_inches = height / dpi[1]

        # Calculate the scaling ratio to fit within the cell while maintaining aspect ratio
        scale_ratio = min(cell_width / width_in_inches, cell_height / height_in_inches)
        new_width = width_in_inches * scale_ratio
        new_height = height_in_inches * scale_ratio

        # Save a resized temporary image
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            img = img.resize((int(new_width * dpi[0]), int(new_height * dpi[1])), Image.LANCZOS)
            img.save(temp_file, format="JPEG", dpi=(dpi[0], dpi[1]))
            temp_file_path = temp_file.name

        # Insert the resized image into the document
        run.add_picture(temp_file_path, width=Inches(new_width), height=Inches(new_height))

        # Clean up the temporary file
        os.remove(temp_file_path)
