from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import design
import camera
import tools

class MainWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.camera: None = None
        self.tools: tools.Tools = tools.Tools()
        self.img_data: list = []
        self.img_data_clone: list = []
        self.get_com_port_number.clicked.connect(self.get_comport)
        self.init_device_button.clicked.connect(self.initialize_device)
        self.get_version_button.clicked.connect(self.output_version)
        self.reset_settings_button.clicked.connect(self.output_reset)
        self.get_photo_size_button.clicked.connect(self.output_photo_size)
        self.choose_path_button.clicked.connect(self.show_dialog)
        self.choose_photo_size.addItem('320x240')
        self.choose_photo_size.addItem('640x480')
        self.choose_photo_compr.addItem('1X')
        self.choose_photo_compr.addItem('2X')
        self.choose_photo_compr.addItem('4X')
        self.set_photo_compression_button.clicked.connect(self.set_compression)
        self.set_photo_size_button.clicked.connect(self.set_photo_size)
        self.take_photo_button.clicked.connect(self.take_snap)

        self.figure = Figure(tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.image_layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)

    def initialize_device(self) -> None:
        self.camera: camera.Camera = camera.Camera(port = self.get_com_port_text.text())
        self.init_device_alert.setText("Success!")

    def get_comport(self) -> None:
        self.get_com_port_text.setText(self.tools.find_comport())

    def output_version(self) -> None:
        self.get_version_output.setText(self.camera.get_version())

    def output_reset(self) -> None:
        if self.camera.reset() is not None:
            self.reset_settings_text.setText("Reset done!")

    def output_photo_size(self) -> None:
        self.get_photo_size_text.setText(str(self.camera.get_fbuf_len()))

    def take_snap(self) -> list:
        self.camera.take_photo()
        self.img_data = self.camera.read_fbuf(self.camera.get_fbuf_len())
        self.take_photo_alert.setText('Success')
        self._remove_image()
        self.plot_image()
        self.img_data_clone[:] = self.img_data
        self.img_data[:] = []

    def show_dialog(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Choose saving path", "", "All files (*);;JPEG files (*.jpg)", options=options)
        self.camera.save_photo(self.img_data_clone, file_name+'.jpg')

    def set_compression(self) -> None:
        text: str = self.choose_photo_compr.currentText()
        self.camera.COMPRESSION_RATIO = self.camera.set_compr_ratio(text)
        self.camera.set_photo_compression()
        print('ratio set')

    def set_photo_size(self) -> None:
        text: str = self.choose_photo_size.currentText()
        self.camera.PHOTO_SIZE = self.camera.choose_photo_size(text)
        self.camera.set_photo_size()
        print('size set')

    def _remove_image(self) -> None:
        self.image_layout.removeWidget(self.canvas)
        self.canvas.deleteLater()
        self.canvas = None
        self.ax.clear()

    def plot_image(self) -> None:
        self.canvas = FigureCanvas(self.figure)
        self.image_layout.addWidget(self.canvas)
        data: bytearray = self.camera.prepare_photo(self.img_data)
        self.ax.imshow(data)
        self.canvas.draw()

def main() -> None:
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
