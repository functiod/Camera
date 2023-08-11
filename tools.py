import serial
import serial.tools.list_ports

class Tools():
    "Additional Camera0706 tools"

    device_description: str = 'Silicon Labs CP210x USB to UART Bridge'

    def __init__(self) -> None:
        pass

    def find_com_port_name(self) -> str:
        comports: list = [port.description for port in serial.tools.list_ports.comports()]
        description: str = [comport for comport in comports if self.device_description in comport][0]
        port_name: str = description[description.find("COM"):-1]
        return port_name

    def set_compr_ratio(self, ratio: str) -> int:
        ratio_dict: dict = {
            '1X' : 0x36,
            '2X' : 0x72,
            '4X' : 0xFF
        }
        return ratio_dict[ratio]

    def choose_photo_size(self, size: str) -> int:
        size_dict: dict = {
            '320x240' : 0x00,
            '640x480' : 0x11
        }
        return size_dict[size]

