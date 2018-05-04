import os
from configparser import ConfigParser
import traceback

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.Qt as qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal
from pandas import DataFrame

from gui.widgets.MainWindow import MainWindow
from analyzer.analyzer import Analyzer
from common.predict import Predict

import resources.splashscreen
import resources.icon


class GUI(qc.QObject):

    error_occurred = pyqtSignal(str)
    file_loaded = pyqtSignal(str, str, int)
    analyzed = pyqtSignal(DataFrame, str)

    def __init__(self, config: ConfigParser, analyzer: Analyzer):
        super(GUI, self).__init__()
        self.analyzer = analyzer
        self.config = config
        # Initializing main window
        self.main_window = MainWindow(config=config)
        self.main_window.setWindowTitle("ATC: Automatic Text Classifier v{}".format(
                                        config.get("App", "version")))
        self.main_window.setWindowIcon(QIcon(":/icon.ico"))
        self.main_window.app_info_window_request.connect(self.invoke_info_widget)
        self.main_window.export_request.connect(self.export)
        self.main_window.analyze_request.connect(self.analyze)
        # Connecting analyzer interface signals
        self.analyzer.error_occurred.connect(self.main_window.console.printErrorMessage)
        self.analyzer.info_message.connect(self.main_window.console.printInfoMessage)
        self.analyzer.warning_message.connect(self.main_window.console.printWarningMessage)
        self.analyzer.complete.connect(self.on_analysis_completed)
        # Shou da windu!
        self.main_window.showMaximized()

    def invoke_info_widget(self):
        self.main_window.display_info_window(self.analyzer)

    def analyze(self):
        try:
            text = self.main_window.text_widget.get_input()
            if text == "":
                return
            params = self.main_window.opt_bar.options_to_dict()
            # self.main_window.setCursor(qt.Qt.WaitCursor)
            self.analyzer.analyzeInParallel(text=text, params=params)
        except Exception as e:
            print(e)
            traceback.print_exc()

    def export(self):
        try:
            result = self.main_window.result_widget.last_result
            if result is None:
                return
            filename = self.main_window.save_dialog.getSaveFileName(filter="*.txt")[0]
            if not filename:
                return
            threshold = self.main_window.opt_bar.threshold.value()
            result.save_to_file(filename=filename, threshold=threshold)
        except Exception as e:
            self.error_occurred.emit("Не удалось экспортировать результат")

    def on_analysis_completed(self, result: Predict):
        params = self.main_window.opt_bar.options_to_dict()
        self.main_window.result_widget.show_output(result, params)


def show_splashscreen():
    splash = qw.QSplashScreen(QPixmap(":/Splash_email_v2.png"), qc.Qt.WindowStaysOnTopHint)
    time = qc.QTime()
    splash.show()
    time.start()
    while time.elapsed() <= 3000:
        pass
    splash.finish(None)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    from configparser import ConfigParser

    a = QApplication(sys.argv)
    c = ConfigParser()
    c.read("../config.ini")
    g = GUI(config=c, analyzer=Analyzer(c))
    a.exec()
