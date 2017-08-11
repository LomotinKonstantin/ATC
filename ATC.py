from argparse import ArgumentParser
import sys

from imports.config import Config
from imports.ui import UI
from PyQt5.QtWidgets import QApplication


class ATC:
    config = Config()
    # Just a stub. Static fields initialize before main code is run
    # So QApplication isn't launched yet and it crashes the app
    ui = []

    def __init__(self):
        # initialising fields
        self.parameters = {}
        # loading config
        self.config.load()
        # selecting mode
        if len(sys.argv) > 1:
            self._parse_args()
        else:
            self.ui = UI()
            self.ui.launch()


    def _parse_args(self):
        description = "Automated Text Classifier for VINITI. Чтобы запустить графический сеанс, " \
                      "запустите программу без аргументов"
        argparser = ArgumentParser(prog="ATC", description=description)
        argparser.add_argument("-i", "--input", help="полный путь к файлу с текстом", required=True)
        argparser.add_argument("-o", "--output",
                               help="полный путь к файлу, в который будет записан результат",
                               required=True)
        argparser.add_argument("-id",
                               "--rubricator-id",
                               help="идентификатор рубрикатора",
                               choices=self.config.get(self.config.ID_OPTION),
                               required=True)
        argparser.add_argument("-f", "--format", help="формат входного файла",
                               choices=self.config.get(self.config.FORMAT_OPTION),
                               required=True)
        argparser.add_argument("-l", "--language", help="язык входного текста",
                               choices=self.config.get(self.config.LANG_OPTION),
                               required=True)
        argparser.add_argument("-t", "--threshold", help="пороговое значение вероятности. " +
                                                         "Ответы классификатора с вероятностью ниже " +
                                                         "заданной выведены не будут",
                               default=0.0,
                               type=float,
                               required=False)
        self.parameters = vars(argparser.parse_args())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = ATC()
    sys.exit(app.exec())
