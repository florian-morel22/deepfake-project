import io

from PIL import Image

def Image2bytes(image: Image.Image):


    image_bytes_io = io.BytesIO()
    image.save(image_bytes_io, format="JPEG")
    image_bytes = image_bytes_io.getvalue()

    return image_bytes
