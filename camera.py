import time
import serial
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import array
from datetime import datetime
import io

TIMEOUT = 0.5
SENDSIGN = 0x56
SERIALNUM = 0x00
RETURNSIGN = 0x76
DATALENGTH = 0X00

CMD_GETVERSION = 0x11
CMD_RESET = 0x26
CMD_TAKEPHOTO = 0x36
CMD_READBUFF = 0x32
CMD_GETBUFFLEN = 0x34
CMD_SETBAUDRATE = 0x24
CMD_GET_COMPRESS_RATIO = 0x30
CMD_SET_COMPRESS_RATIO = 0x31

FBUF_STOPCURRENTFRAME = 0x00
FBUF_CURRENTFRAME = 0x00
FBUF_NEXTFRAME = 0x01
FBUF_CTRL = 0x01

VC0706_320_240 = 0x11
VC0706_640_480 = 0x00

VC0706_READ_DATA = 0x30
VC0706_WRITE_DATA = 0x31

COMPRESSION_RATIO = 0x36

get_version_cmd: list = [SENDSIGN, SERIALNUM, CMD_GETVERSION, DATALENGTH]
reset_cmd: list = [SENDSIGN, SERIALNUM, CMD_RESET, DATALENGTH]
take_photo_cmd: list = [SENDSIGN, SERIALNUM, CMD_TAKEPHOTO, FBUF_CTRL, FBUF_STOPCURRENTFRAME]
get_buff_len_cmd: list = [SENDSIGN, SERIALNUM, CMD_GETBUFFLEN, FBUF_CTRL, FBUF_CURRENTFRAME]
get_compression_ratio_cmd: list = [SENDSIGN, SERIALNUM, CMD_GET_COMPRESS_RATIO, 0x04, 0x01, 0x01, 0x12, 0x04]
set_compression_ratio_cmd: list = [SENDSIGN, SERIALNUM, CMD_SET_COMPRESS_RATIO, 0x05, 0x01, 0x01, 0x12, 0x04, COMPRESSION_RATIO]
set_photo_size_cmd: list = [SENDSIGN, SERIALNUM, VC0706_WRITE_DATA, 0x05, 0x04, 0x01, 0x00, 0x19, VC0706_640_480]
read_photo_cmd: list = [SENDSIGN, SERIALNUM, CMD_READBUFF, 0x0c, FBUF_CURRENTFRAME, 0x0a]

class Camera:
    "Class representing a VC0706 camera"

    defualt_baud_rate: int = 38400
    com_port: str = 'COM6'
    data_length_elem = 4
    bytes_to_read: int = 1024
    photos_folder_name: str = 'Photos'
    num_start_jpg_digits: int = 5
    num_end_jpg_digits: int = 5

    def __init__(self, port: str = com_port, baud_rate: int = defualt_baud_rate) -> None:
        self.camera = serial.Serial(port, baud_rate)
        self.image_photo: list = []

    def get_version(self) -> str:
        self.camera.write(bytes(get_version_cmd))
        time.sleep(TIMEOUT)
        camera_version: str | None = self.camera.read_all().decode("utf-8")
        return camera_version

    def reset(self) -> str:
        self.camera.write(bytes(reset_cmd))
        time.sleep(TIMEOUT)
        basic_conf_info: str | None = self.camera.read_all().decode("utf-8")
        return basic_conf_info

    def set_photo_compression(self) -> list:
        self.camera.write(bytes(set_compression_ratio_cmd))
        time.sleep(TIMEOUT)
        self.camera.write(bytes(get_compression_ratio_cmd))
        time.sleep(TIMEOUT)
        compression_ratio: list = list(map(hex, list(self.camera.read_all())))
        return compression_ratio

    def get_fbuf_len(self) -> int:
        self.camera.write(bytes(get_buff_len_cmd))
        time.sleep(TIMEOUT)
        fbuf_length: list = np.frombuffer(self.camera.read_all(), dtype=np.uint8)[-self.data_length_elem:]
        length: int = 0
        for i in range(self.data_length_elem):
            length |= fbuf_length[i] << 8*(self.data_length_elem - 1 - i)
        return length

    def set_photo_size(self) -> None:
        self.camera.write(bytes(set_photo_size_cmd))
        time.sleep(TIMEOUT)

    def take_photo(self) -> None:
        self.set_photo_compression()
        self.camera.write(bytes(take_photo_cmd))
        time.sleep(TIMEOUT)

    def __prepare_command(self, read_bytes: int, initial_adr: int = 0) -> bytes:
        command: list = read_photo_cmd + [(initial_adr >> 24) & 0xff, (initial_adr >> 16) & 0xff, (initial_adr >> 8) & 0xff, initial_adr & 0xff]
        command += [(read_bytes >> 24) & 0xff, (read_bytes >> 16) & 0xff, (read_bytes >> 8) & 0xff, read_bytes & 0xff]
        command += [1, 0]
        final_cmd: bytes = array.array('B', command).tobytes()
        return final_cmd

    def read_fbuf(self, my_bytes: bytes) -> list:
        initial_offset: bytes = 0
        data: bytes = 0
        while(initial_offset < my_bytes):
            bytes_to_get: int = min(my_bytes - initial_offset, self.bytes_to_read)
            command: bytes = self.__prepare_command(bytes_to_get, initial_offset)
            self.camera.write(command)
            time.sleep(TIMEOUT)
            initial_offset += bytes_to_get
            data_len: int = self.num_start_jpg_digits + bytes_to_get + self.num_end_jpg_digits
            if bytes_to_get >= 1024:
                data = self.camera.read(data_len)
            else:
                data = self.camera.read_all()
            reply: bytes = list(data)
            self.image_photo += reply[self.num_start_jpg_digits:bytes_to_get + self.num_end_jpg_digits]
        return self.image_photo

    def save_photo(self) -> None:
        photodata: bytes = array.array('B', self.image_photo).tobytes()
        to_file: str = datetime.now().strftime(f"{self.photos_folder_name}\\%m-%d-%Y_%H-%M-%S_photo.jpg")
        with open(to_file, 'wb') as photo_file:
            photo_file.write(photodata)

    def plot_photo(self, data: list) -> None:
        image_data = io.BytesIO(data)
        with image_data:
            image: np.ndarray = mpimg.imread(image_data, format='jpeg')
        plt.imshow(image)
        plt.show()

if __name__ == '__main__':
    camera: Camera = Camera()
    camera.reset()
    camera.set_photo_compression()
    camera.set_photo_size()
    camera.take_photo()
    bytes_to_read: int = camera.get_fbuf_len()
    print("Bytes to read", bytes_to_read)
    camera.read_fbuf(bytes_to_read)
    camera.save_photo()
    camera.plot_photo(array.array('B', camera.image_photo).tobytes())
