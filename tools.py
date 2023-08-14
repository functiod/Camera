import serial
import serial.tools.list_ports

class Tools():
    "Additional Camera0706 tools"

    device_description: str = 'Silicon Labs CP210x USB to UART Bridge'

    def __init__(self) -> None:
        pass

    def find_comport(self) -> str | None:
        ports: list = serial.tools.list_ports.comports()
        for name in (ports):
            if self.device_description in name.description:
                return name.device
        return None

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

if __name__ == "__main__":
    tools = Tools()
    print(tools.find_comport())
