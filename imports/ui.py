import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
from PyQt5.QtGui import QIcon

from imports.widgets.MainWidget import MainWidget
from imports.widgets.ControlWidget import ControlWidget


class UI(qw.QMainWindow):

    def __init__(self, config):
        super().__init__()
        self.setMinimumSize(qc.QSize(800, 600))
        self.setWindowTitle("ATC: Automatic Text Classifier")
        self.setWindowIcon(QIcon("icon.ico"))
        # Toolbar
        toolbar = ControlWidget()
        self.addToolBar(toolbar)
        self.setCentralWidget(MainWidget(config))
        # Menu bar
        menu = qw.QMenuBar()
        self.setMenuBar(menu)

        file_menu = menu.addMenu("Файл")
        file_menu.addAction(toolbar.open_action)
        toolbar.open_action.triggered.connect(self.open_file)
        file_menu.addAction(toolbar.export_action)

    def open_file(self):
        file_dialog = qw.QFileDialog()
        filename = file_dialog.getOpenFileName()[0]


    def launch(self):
        self.show()
