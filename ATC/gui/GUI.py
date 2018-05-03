import os
from configparser import ConfigParser

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal
from pandas import DataFrame

from gui.widgets.MainWindow import MainWindow
from analyzer.analyzer import Analyzer

import resources.splashscreen
import resources.icon


class GUI(qc.QObject):

    error_occurred = pyqtSignal(str)
    file_loaded = pyqtSignal(str, str, int)
    analyzed = pyqtSignal(DataFrame, str)

    def __init__(self, config: ConfigParser, analyzer: Analyzer):
        super(GUI, self).__init__()
        # Initializing main window
        self.main_window = MainWindow(config=config)
        self.main_window.setWindowTitle("ATC: Automatic Text Classifier v{}".format(
                                        config.get("App", "version")))
        self.main_window.setWindowIcon(QIcon(":/icon.ico"))
        self.analyzer = analyzer
        self.config = config
        self.main_window.app_info_window_request.connect(self.invoke_info_widget)
        self.main_window.export_request.connect(self.export)
        # Connecting analyzer interface signals
        self.analyzer.language_recognized.connect(self.main_window.on_language_recognized)
        self.analyzer.error_occurred.connect(self.main_window.console.printErrorMessage)
        self.analyzer.info_message.connect(self.main_window.console.printInfoMessage)
        self.analyzer.warning_message.connect(self.main_window.console.printWarningMessage)
        # Shou da windu!
        self.main_window.showMaximized()


    def invoke_info_widget(self):
        self.main_window.display_info_window(self.analyzer)

    def analyze(self):
        pass
        # try:
        #     lw = LoadingWidget(0, 5)
        #     lw.show()
        #     text = self.main_widget.text_widget.get_input()
        #     if not self.analyzer.valid(text):
        #         return
        #     if len(text) == 0:
        #         return
        #     self.params = self.main_widget.opt_bar.options_to_dict()
        #     if self.changed:
        #         lw.update_state(0, "Инициализируем модули...")
        #         if not self.analyzer.load_modules(self.params,
        #                                           self.main_widget.text_widget.indicate_error):
        #             return
        #     lw.update_state(1, "Анализируем...")
        #     result = self.analyzer.analyze(text, self.params, lw)
        #     if result is None:
        #         # self.main_widget.text_widget.indicate_error("Не удалось предобработать текст")
        #         return
        #     if result.index.name != "id":
        #         if result.loc[0, "result"] is None:
        #             self.main_widget.text_widget.indicate_error("Не удалось определить рубрики")
        #             return
        #     lw.update_state(5, "Готово!")
        #     if self.main_widget.opt_bar.is_description_allowed():
        #         self.analyzed.emit(result, self.params["rubricator_id"])
        #     else:
        #         self.analyzed.emit(result, "")
        # except Exception as e:
        #     print(e)
        #     import traceback
        #     traceback.print_exc()

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
            print(e)


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
