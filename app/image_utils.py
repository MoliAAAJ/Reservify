from io import BytesIO
from PIL import Image
from fastapi import UploadFile
from typing import Optional

def create_thumbnail_from_upload(upload_file: UploadFile, size=(128, 128)) -> Optional[UploadFile]:
    """
    Converts an uploaded file to a thumbnail and returns it as an UploadFile.

    :param upload_file: The uploaded file object (e.g., from a form or API).
    :param size: Tuple indicating the size of the thumbnail, default is (128, 128).
    :return: An UploadFile object representing the thumbnail, or None if an error occurs.
    """
    try:
        # Open the uploaded file as an image
        image_obj = Image.open(upload_file.file)
        # Create a copy of the image to avoid modifying the original
        thumbnail_img = image_obj.copy()
        # Convert to thumbnail
        thumbnail_img.thumbnail(size)
        
        # Save the thumbnail to a BytesIO object
        img_byte_arr = BytesIO()
        thumbnail_img.save(img_byte_arr, format='PNG')  # You can change the format if needed
        img_byte_arr.seek(0)
        
        # Create a new UploadFile object from the BytesIO
        return UploadFile(file=img_byte_arr, filename='thumbnail.png')  # You can change the filename as needed
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None