import numpy as np
import io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import array
from datetime import datetime

class Processing():
    "Class for working with files"

    def __init__(self) -> None:
        pass

    def prepare_photo(self, data: bytes) -> bytearray:
        image_data = io.BytesIO(array.array('B', data).tobytes())
        with image_data:
            image: np.ndarray = mpimg.imread(image_data, format='jpeg')
        return image

    def save_photo(self, data: bytes, path: str) -> None:
        photodata: bytes = array.array('B', data).tobytes()
        # to_file: str = datetime.now().strftime(f"{folder_name}\\%m-%d-%Y_%H-%M-%S_photo.jpg")
        with open(path, 'wb') as photo_file:
            photo_file.write(photodata)
