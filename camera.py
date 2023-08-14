import time
import serial
import numpy as np
import array
import tools
import processing
import settings

class Camera(tools.Tools, processing.Processing):
    "Class representing a VC0706 camera"

    defualt_baud_rate: int = 38400
    com_port: str = 'COM6'
    data_length_elem = 4
    bytes_to_read: int = 1024
    photos_folder_name: str = 'Photos'
    num_start_jpg_digits: int = 5
    num_end_jpg_digits: int = 5
    COMPRESSION_RATIO = 0x36
    PHOTO_SIZE = 0x00

    def __init__(self, port: str = com_port, baud_rate: int = defualt_baud_rate) -> None:
        super().__init__()
        self.camera = serial.Serial(port, baud_rate)
        self.image_photo: list = []

    def get_version(self) -> str:
        self.camera.write(bytes(settings.get_version_cmd))
        time.sleep(settings.TIMEOUT)
        camera_version: str | None = self.camera.read_all().decode("utf-8")
        return camera_version[camera_version.find('V'):]

    def reset(self) -> str:
        self.camera.write(bytes(settings.reset_cmd))
        time.sleep(settings.TIMEOUT)
        basic_conf_info: str | None = self.camera.read_all()
        return list(basic_conf_info)

    def set_photo_compression(self) -> list:
        self.camera.write(bytes(settings.set_compression_ratio_cmd) + self.COMPRESSION_RATIO.to_bytes(1, 'big'))
        time.sleep(settings.TIMEOUT)
        self.camera.write(bytes(settings.get_compression_ratio_cmd))
        time.sleep(settings.TIMEOUT)
        compression_ratio: list = list(map(hex, list(self.camera.read_all())))
        return compression_ratio

    def get_fbuf_len(self) -> int:
        length: int = 0
        self.camera.write(bytes(settings.get_buff_len_cmd))
        time.sleep(settings.TIMEOUT)
        fbuf_length: list = np.frombuffer(self.camera.read_all(), dtype=np.uint8)[-self.data_length_elem:]
        for i in range(self.data_length_elem):
            length |= fbuf_length[i] << 8*(self.data_length_elem - 1 - i)
        return length

    def set_photo_size(self) -> None:
        self.camera.write(bytes(settings.set_photo_size_cmd) + self.PHOTO_SIZE.to_bytes(1, 'big'))
        time.sleep(settings.TIMEOUT)

    def take_photo(self) -> None:
        self.set_photo_compression()
        self.camera.write(bytes(settings.take_photo_cmd))
        time.sleep(settings.TIMEOUT)

    def __prepare_command(self, read_bytes: int, initial_adr: int = 0) -> bytes:
        command: list = settings.read_photo_cmd + [(initial_adr >> 24) & 0xff, (initial_adr >> 16) & 0xff, (initial_adr >> 8) & 0xff, initial_adr & 0xff]
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
            time.sleep(settings.TIMEOUT)
            initial_offset += bytes_to_get
            data_len: int = self.num_start_jpg_digits + bytes_to_get + self.num_end_jpg_digits
            if bytes_to_get >= 1024:
                data = self.camera.read(data_len)
            else:
                data = self.camera.read_all()
            reply: bytes = list(data)
            self.image_photo += reply[self.num_start_jpg_digits:bytes_to_get + self.num_end_jpg_digits]
        return self.image_photo
