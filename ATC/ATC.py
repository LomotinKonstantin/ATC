from argparse import ArgumentParser
import sys
import os
import warnings
from configparser import ConfigParser
import codecs


warnings.filterwarnings('ignore')

from PyQt5.QtWidgets import QApplication

from gui.GUI import GUI, show_splashscreen
from analyzer.analyzer import Analyzer


def unescaped_str(arg_str):
    return codecs.decode(str(arg_str), errors='backslashreplace')

class ATC:

    section = "AvailableOptions"

    def __init__(self):
        # Initialising fields
        self.parameters = {}
        # Loading config
        self.config = self.loadConfig()
        self.analyzer = Analyzer(self.config)
        # Selecting mode
        if len(sys.argv) > 1:
            self.parse_args()
            # self.analyzer.error_occurred.connect(self.print_error)
            filename = self.parameters["input"]
            if not os.path.exists(filename):
                self.print_error("File {} does not exist".format(filename))
                sys.exit()
            try:
                text = self.analyzer.load_file(self.parameters["input"])
                if not self.analyzer.isTextValid(text):
                    self.print_error("File {} does not contain valid text".format(filename))
                    sys.exit()
            except Exception as e:
                self.print_error("Error loading file {}:\n{}".format(filename, e))
                sys.exit()
            result = self.analyzer.analyze(text, self.parameters)
            if result is None:
                self.print_error("Unknown error occurred")
                sys.exit()
            result.saveToFile(self.parameters["output"], self.parameters["threshold"])
            sys.exit(0)
        else:
            show_splashscreen()
            self.ui = GUI(analyzer=self.analyzer, config=self.config)

    def parse_args(self):
        description = "Automated Text Classifier for VINITI. Чтобы запустить графический сеанс, " \
                      "запустите программу без аргументов"
        argparser = ArgumentParser(prog="ATC", description=description)
        ids = self.config.get(self.section, "ids").split(", ")
        formats = self.config.get(self.section, "formats").split(", ")
        languages = self.config.get(self.section, "languages").split(", ")
        argparser.add_argument("-i", "--input",
                               help="полный путь к файлу с текстом",
                               required=True)
        # type=unescaped_str
        argparser.add_argument("-o", "--output",
                               help="полный путь к файлу, в который будет записан результат",
                               required=True)
        argparser.add_argument("-id",
                               "--rubricator-id",
                               help="идентификатор рубрикатора",
                               choices=ids,
                               required=True)
        argparser.add_argument("-f", "--format", help="формат входного файла",
                               choices=formats,
                               required=False)
        argparser.add_argument("-l", "--language", help="язык входного текста",
                               choices=languages,
                               required=True)
        argparser.add_argument("-t", "--threshold", help="пороговое значение вероятности. " +
                                                         "Ответы классификатора с вероятностью ниже " +
                                                         "заданной выведены не будут",
                               default=0.0,
                               type=float,
                               required=False)
        self.parameters = vars(argparser.parse_args())

    def print_error(self, error_msg: str):
        print(error_msg, file=sys.stderr)

    def loadConfig(self):
        parser = ConfigParser()
        parser.read(["config.ini"], encoding="utf-8")
        return parser


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = ATC()
    sys.exit(app.exec())
