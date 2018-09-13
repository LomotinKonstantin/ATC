from argparse import ArgumentParser, Action
import sys
import os
import warnings
from configparser import ConfigParser
import codecs

warnings.filterwarnings('ignore')

from PyQt5.QtWidgets import QApplication

from gui.GUI import GUI, show_splashscreen
from analyzer.analyzer import Analyzer
from shutil import copyfile


def unescaped_str(arg_str):
    return codecs.decode(str(arg_str), errors='backslashreplace')


class PrintModels(Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(PrintModels, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        path = os.path.join(os.path.dirname(__file__),
                            "analyzer",
                            "modules",
                            "classifier",
                            "config.ini")
        config = ConfigParser()
        config.read(path)
        for i in config.options("Settings"):
            print(i, config.get("Settings", i))


class SetModels(Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(SetModels, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        path = os.path.join(os.path.dirname(__file__),
                            "analyzer",
                            "modules",
                            "classifier",
                            "config.ini")
        config = ConfigParser()
        config.read(path)
        lang = ""
        rubr = ""
        if "ru" in values:
            lang = "ru"
        elif "en" in values:
            lang = "en"
        else:
            print("Неверный формат имени файла")
            exit()
        if "rgnti" in values:
            rubr = "RGNTI"
        elif "subj" in values:
            rubr = "SUBJ"
        elif "ipv" in values:
            rubr = "IPV"
        else:
            print("Неверный формат имени файла")
            exit()
        option = "{}_{}".format(rubr, lang)
        config.set("Settings", option, values)
        with open(path, "w") as fp:
            config.write(fp)
        print("Done")


class RestoreAction(Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(RestoreAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        mapping = {
            "classifier": "classifier",
            "we": "word_embedding",
            "preprocessor": "preprocessor"
        }
        if values not in mapping.keys():
            print("Что-то сильно пошло не так. Разработчики будут не в восторге :\\")
            exit()
        src = os.path.join(os.path.dirname(__file__),
                           "analyzer", "backup",
                           "{}_config.ini".format(values))
        dst = os.path.join(os.path.dirname(__file__),
                           "analyzer", "modules",
                           mapping[values], "config.ini")
        copyfile(src, dst)
        print("Done")


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
            result.save_to_file(self.parameters["output"], self.parameters["threshold"])
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
        # Creating command CLI group
        subparsers = argparser.add_subparsers(help="Commands")
        get_parser = subparsers.add_parser("get",
                                           help="Получить значение параметра")
        get_parser.add_argument("type", help="параметр",
                                choices=["plk"],
                                action=PrintModels)
        set_parser = subparsers.add_parser("set", help="установить значение параметра")
        set_subs = set_parser.add_subparsers(help="Setters")
        plk_setter = set_subs.add_parser("plk")
        plk_setter.add_argument("file",
                                help="имя файла модели классификатора (*.plk)",
                                action=SetModels)
        restore_parser = subparsers.add_parser("restore")
        restore_parser.add_argument("target",
                                    help="какой файл конфигурации восстановить",
                                    choices=["classifier"],
                                    action=RestoreAction)

        self.parameters = vars(argparser.parse_args())

    def print_error(self, error_msg: str):
        print(error_msg, file=sys.stderr)

    def loadConfig(self):
        parser = ConfigParser()
        parser.read([os.path.join(os.path.dirname(__file__), "config.ini")], encoding="utf-8")
        return parser


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = ATC()
    sys.exit(app.exec())
