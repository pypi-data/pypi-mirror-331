import os


def get_images_from_folder(folder):
    """Returns a list of image file paths from the given folder, including .thumb files."""
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".thumb")
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(valid_extensions)]
