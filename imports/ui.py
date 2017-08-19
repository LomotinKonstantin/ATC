import os

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal

from imports.widgets.MainWidget import MainWidget
from imports.widgets.ControlWidget import ControlWidget
from imports.widgets.ModuleManager import ModuleManager


class UI(qw.QMainWindow):

    error_occurred = pyqtSignal(str)
    file_loaded = pyqtSignal(str, str, int)
    analyzed = pyqtSignal(dict)

    def __init__(self, config, analyzer=None):
        super().__init__()
        self.setMinimumSize(qc.QSize(800, 600))
        self.setWindowTitle("ATC: Automatic Text Classifier")
        self.setWindowIcon(QIcon("icon.ico"))
        self.analyzer = analyzer
        self.config = config
        self.status_label = qw.QLabel()
        self.statusBar().addWidget(self.status_label)
        # File dialogs
        self.load_dialog = qw.QFileDialog()
        self.save_dialog = qw.QFileDialog()
        # Toolbar
        self.toolbar = ControlWidget()
        self.addToolBar(self.toolbar)
        self.main_widget = MainWidget(config)
        self.main_widget.set_font_size(int(self.config.get(self.config.FONT_OPTION)))
        self.setCentralWidget(self.main_widget)
        # Module dialog
        self.module_manager = ModuleManager(analyzer, config, self.main_widget)
        self.module_manager.exec()
        # Menu bar
        menu = qw.QMenuBar()
        self.setMenuBar(menu)

        file_menu = menu.addMenu("Файл")
        file_menu.addAction(self.toolbar.open_action)
        file_menu.addAction(self.toolbar.export_action)

        font_menu = menu.addMenu("Шрифт")
        group = qw.QActionGroup(self)
        for i in range(8, 21):
            action = qw.QAction(QIcon(), str(i), self)
            action.setCheckable(True)
            if i == self.main_widget.font_size:
                action.setChecked(True)
            action.setActionGroup(group)
            font_menu.addAction(action)
            action.triggered.connect(self.font_size_selected)

        # Signals
        self.toolbar.open_action.triggered.connect(self.read_file)
        self.toolbar.analyze_action.triggered.connect(self.analyze)
        self.toolbar.export_action.triggered.connect(self.export)
        self.error_occurred.connect(self.main_widget.text_widget.indicate_error)
        self.file_loaded.connect(self.main_widget.text_widget.show_text)
        self.file_loaded.connect(self.set_status)
        if analyzer:
            self.analyzer.import_error_occured.connect(self.process_import_error)
        self.analyzed.connect(self.main_widget.text_widget.show_output)

    def read_file(self):
        filename = self.load_dialog.getOpenFileName()[0]
        if not filename:
            return
        try:
            content = self.analyzer.load_file(filename)
            self.file_loaded.emit(content, filename, os.path.getsize(filename))
        except:
            self.error_occurred.emit("Не удалось прочитать текст из файла!")

    def set_status(self, content, filename, size):
        self.status_label.setText(
            filename + "\t" + "(" + str(size) + " байт)\t" + str(len(content)) + " символов"
        )

    def set_analyzer(self, analyzer):
        self.analyzer = analyzer
        self.analyzer.import_error_occured.connect(self.process_import_error)

    def analyze(self):
        text = self.main_widget.text_widget.get_input()
        if len(text) == 0:
            return
        result = self.analyzer.analyze(text)
        self.analyzed.emit(result)

    def font_size_selected(self):
        size = int(self.sender().text())
        self.main_widget.set_font_size(size)
        self.config.set(self.config.FONT_OPTION, size)
        self.config.save()

    def launch(self):
        self.showMaximized()

    def export(self):
        result = self.main_widget.text_widget.get_output()
        if not result:
            return
        filename = self.save_dialog.getSaveFileName(filter="*.txt")[0]
        self.analyzer.export(result, filename)

    def process_import_error(self, msg):
        self.main_widget.text_widget.indicate_error(msg)
        self.toolbar.analyze_action.setEnabled(False)