import os

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal
from pandas import DataFrame

from imports.widgets.MainWidget import MainWidget
from imports.widgets.ControlWidget import ControlWidget
from imports.widgets.ModuleManager import ModuleManager
from imports.widgets.LoadingWidget import LoadingWidget
import imports.splashscreen


class UI(qw.QMainWindow):

    error_occurred = pyqtSignal(str)
    file_loaded = pyqtSignal(str, str, int)
    analyzed = pyqtSignal(DataFrame, str)

    def __init__(self, config, analyzer=None):
        super().__init__()
        self.setMinimumSize(qc.QSize(800, 600))
        self.setWindowTitle("ATC: Automatic Text Classifier v" + config.get(config.VERSION_OPTION))
        self.setWindowIcon(QIcon("icon.ico"))
        self.analyzer = analyzer
        self.config = config
        self.status_label = qw.QLabel()
        self.lang_label = qw.QLabel()
        self.statusBar().addWidget(self.status_label)
        self.statusBar().addWidget(self.lang_label)
        self.changed = True
        # File dialogs
        self.load_dialog = qw.QFileDialog()
        self.save_dialog = qw.QFileDialog()
        # Toolbar
        self.toolbar = ControlWidget()
        self.addToolBar(self.toolbar)
        self.main_widget = MainWidget(config)
        self.main_widget.set_font_size(int(self.config.get(self.config.FONT_OPTION)))
        self.setCentralWidget(self.main_widget)
        self.params = self.main_widget.opt_bar.options_to_dict()
        # Module dialog
        self.module_manager = ModuleManager(analyzer, config, self.main_widget)
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
        # self.toolbar.analyze_action.triggered.connect(self.main_widget.opt_bar.on_commited)
        self.toolbar.export_action.triggered.connect(self.export)
        self.toolbar.modules_action.triggered.connect(self.module_manager.exec)
        self.error_occurred.connect(self.main_widget.text_widget.indicate_error)
        self.file_loaded.connect(self.main_widget.text_widget.show_text)
        self.file_loaded.connect(self.set_status)
        if analyzer:
            self.analyzer.import_error_occurred.connect(self.process_import_error)
            self.analyzer.error_occurred.connect(self.main_widget.text_widget.indicate_error)
            self.analyzer.language_recognized.connect(self.set_language)
        self.analyzed.connect(self.main_widget.text_widget.show_output)
        self.analyzed.connect(self.lower_changed_flag)
        self.main_widget.opt_bar.description.stateChanged.connect(self.update_output)
        self.main_widget.opt_bar.threshold.valueChanged.connect(self.update_output)
        self.main_widget.opt_bar.state_changed.connect(self.raise_changed_flag)
        self.module_manager.module_changed.connect(self.raise_changed_flag)

        # Launch
        self.showMaximized()

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

    def set_language(self, lang, is_auto=False):
        if is_auto:
            a = " (auto)"
        else:
            a = ""
        self.lang_label.setText(lang + a)

    def set_analyzer(self, analyzer):
        self.analyzer = analyzer
        self.analyzer.import_error_occured.connect(self.process_import_error)

    def analyze(self):
        try:
            lw = LoadingWidget(0, 5)
            lw.show()
            text = self.main_widget.text_widget.get_input()
            if not self.analyzer.valid(text):
                return
            if len(text) == 0:
                return
            self.params = self.main_widget.opt_bar.options_to_dict()
            if self.changed:
                lw.update_state(0, "Инициализируем модули...")
                if not self.analyzer.load_modules(self.params,
                                                  self.main_widget.text_widget.indicate_error):
                    return
            lw.update_state(1, "Анализируем...")
            result = self.analyzer.analyze(text, self.params, lw)
            if result is None:
                # self.main_widget.text_widget.indicate_error("Не удалось предобработать текст")
                return
            if result.index.name != "id":
                if result.loc[0, "result"] is None:
                    self.main_widget.text_widget.indicate_error("Не удалось определить рубрики")
                    return
            lw.update_state(5, "Готово!")
            if self.main_widget.opt_bar.is_description_allowed():
                self.analyzed.emit(result, self.params["rubricator_id"])
            else:
                self.analyzed.emit(result, "")
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()

    def font_size_selected(self):
        size = int(self.sender().text())
        self.main_widget.set_font_size(size)
        self.config.set(self.config.FONT_OPTION, size)
        self.config.save()

    def export(self):
        result = self.main_widget.text_widget.get_output()
        if result is None:
            return
        filename = self.save_dialog.getSaveFileName(filter="*.txt")[0]
        if not filename:
            return
        self.params["threshold"] = self.main_widget.opt_bar.threshold.value()
        self.analyzer.export(result, filename, self.params)

    def process_import_error(self, msg):
        self.main_widget.text_widget.indicate_error(msg)
        self.toolbar.analyze_action.setEnabled(False)

    def update_output(self, state):
        res = self.main_widget.text_widget.last_result
        if res is None:
            return
        if isinstance(state, int):
            st = state
        elif isinstance(state, float):
            st = self.main_widget.opt_bar.description.checkState()
        if st == 2:
            self.main_widget.text_widget.show_output(res, self.params["rubricator_id"])
        else:
            self.main_widget.text_widget.show_output(res, "")

    def raise_changed_flag(self):
        self.changed = True

    def lower_changed_flag(self):
        self.changed = False


def show_splashscreen():
    splash = qw.QSplashScreen(QPixmap(":/Splash_email_v2.png"), qc.Qt.WindowStaysOnTopHint)
    time = qc.QTime()
    splash.show()
    time.start()
    i = 0
    while time.elapsed() <= 3000:
        pass
    splash.finish(None)
