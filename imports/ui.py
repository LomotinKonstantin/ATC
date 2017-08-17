import os

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal

from imports.widgets.MainWidget import MainWidget
from imports.widgets.ControlWidget import ControlWidget


class UI(qw.QMainWindow):

    error_occurred = pyqtSignal(str)
    file_loaded = pyqtSignal(str, str, int)
    analyzed = pyqtSignal(dict)

    def __init__(self, config, analyzer):
        super().__init__()
        self.setMinimumSize(qc.QSize(800, 600))
        self.setWindowTitle("ATC: Automatic Text Classifier")
        self.setWindowIcon(QIcon("icon.ico"))
        self.analyzer = analyzer
        self.status_label = qw.QLabel()
        self.statusBar().addWidget(self.status_label)
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
        toolbar.analyze_action.triggered.connect(self.analyze)
        self.error_occurred.connect(self.main_widget.text_widget.indicate_error)
        self.file_loaded.connect(self.main_widget.text_widget.show_text)
        self.file_loaded.connect(self.set_status)
        self.analyzer.import_error_occured.connect(self.main_widget.text_widget.indicate_error)
        self.analyzed.connect(self.main_widget.text_widget.show_output)

    def read_file(self):
        file_dialog = qw.QFileDialog()
        filename = file_dialog.getOpenFileName()[0]
        try:
            content = self.analyzer.load_file(filename)
            self.file_loaded.emit(content, filename, os.path.getsize(filename))
        except:
            self.error_occurred.emit("Не удалось прочитать текст из файла!")

    def set_status(self, content, filename, size):
        self.status_label.setText(
            filename + "\t" + "(" + str(size) + " байт)\t" + str(len(content)) + " символов"
        )

    def analyze(self):
        text = self.main_widget.text_widget.get_input()
        if len(text) == 0:
            return
        result = self.analyzer.analyze(text)
        self.analyzed.emit(result)
        print("huh")

    def launch(self):
        self.showMaximized()
