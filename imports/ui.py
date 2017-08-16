import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal

from imports.widgets.MainWidget import MainWidget
from imports.widgets.ControlWidget import ControlWidget


class UI(qw.QMainWindow):

    error_occurred = pyqtSignal(str)
    file_loaded = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.setMinimumSize(qc.QSize(800, 600))
        self.setWindowTitle("ATC: Automatic Text Classifier")
        self.setWindowIcon(QIcon("icon.ico"))
        # Toolbar
        toolbar = ControlWidget()
        self.addToolBar(toolbar)
        self.main_widget = MainWidget(config)
        self.setCentralWidget(self.main_widget)
        # Menu bar
        menu = qw.QMenuBar()
        self.setMenuBar(menu)

        file_menu = menu.addMenu("Файл")
        file_menu.addAction(toolbar.open_action)
        file_menu.addAction(toolbar.export_action)
        # Signals
        toolbar.open_action.triggered.connect(self.read_file)
        self.error_occurred.connect(self.main_widget.text_widget.indicate_error)
        self.file_loaded.connect(self.main_widget.text_widget.show_text)

    def read_file(self):
        file_dialog = qw.QFileDialog()
        filename = file_dialog.getOpenFileName()[0]
        try:
            content = open(filename).read()
            self.file_loaded.emit(content)
            return content
        except:
            self.error_occurred.emit("Невозможно загрузить файл!")

    def launch(self):
        self.showMaximized()
