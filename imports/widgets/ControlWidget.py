import PyQt5.QtWidgets as qw
from PyQt5.QtGui import QIcon

import imports.widgets.tool_icons


class ControlWidget(qw.QToolBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.analyze_action = qw.QAction(QIcon(":/lamp.png"), "Анализировать", self)
        self.addAction(self.analyze_action)
        self.open_action = qw.QAction(QIcon(":/import.png"), "Открыть файл", self)
        self.addAction(self.open_action)
        self.export_action = qw.QAction(QIcon(":/save.png"), "Экспорт результата", self)
        self.addAction(self.export_action)
        self.config_action = qw.QAction(QIcon(":/settings.png"), "Параметры конфигурации", self)
        self.addAction(self.config_action)
        self.modules_action = qw.QAction(QIcon(":/exchange.png"), "Менеджер модулей", self)
        self.addAction(self.modules_action)
        self.help_action = qw.QAction(QIcon(":/notepad.png"), "Помощь", self)
        self.addAction(self.help_action)


