import PyQt5.QtWidgets as qw
from PyQt5.QtGui import QIcon, QKeySequence

import imports.widgets.tool_icons


class ControlWidget(qw.QToolBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.analyze_action = qw.QAction(QIcon(":/lamp.png"), "Анализировать", self)
        self.analyze_action.setShortcut(QKeySequence("CTRL+R"))
        self.addAction(self.analyze_action)
        self.open_action = qw.QAction(QIcon(":/import.png"), "Открыть", self)
        self.open_action.setShortcut(QKeySequence("CTRL+O"))
        self.addAction(self.open_action)
        self.export_action = qw.QAction(QIcon(":/save.png"), "Экспорт результата", self)
        self.export_action.setShortcut(QKeySequence("CTRL+S"))
        self.addAction(self.export_action)
        # What should we edit in setting?...
        # self.config_action = qw.QAction(QIcon(":/settings.png"), "Параметры конфигурации", self)
        # self.addAction(self.config_action)
        self.modules_action = qw.QAction(QIcon(":/exchange.png"), "Менеджер модулей", self)
        self.addAction(self.modules_action)
        # Maybe later?...
        # self.help_action = qw.QAction(QIcon(":/notepad.png"), "Помощь", self)
        # self.addAction(self.help_action)


