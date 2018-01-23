import PyQt5.QtWidgets as qw
from PyQt5.Qt import QFont, QIcon
from PyQt5.QtCore import pyqtSignal

from gui.widgets.OptionPane import OptionPane
from gui.widgets.TextWidget import TextWidget
from gui.widgets.PredictTableWidget import PredictTableWidget
from gui.widgets.ToolBar import ToolBarWidget
from gui.widgets.ConsoleWidget import ConsoleWidget

###
### TODO: make this class the main widget inherited from QMainWindow
###


class MainWindow(qw.QMainWindow):
    font_family = "Segoe"
    font_size_selected = pyqtSignal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        # Setting the layout
        layout = qw.QGridLayout()
        self.setLayout(layout)
        # Setting the side option bar
        self.opt_bar = OptionPane(config, parent=self)
        layout.addWidget(self.opt_bar, 0, 6, 3, 2)
        # Setting the text widget
        self.text_widget = TextWidget(self.opt_bar, parent=self)
        layout.addWidget(self.text_widget, 0, 0, 3, 6)
        # Creating the menu bar
        ### TODO: signals
        self.createMenu()
        # Setting the status bar
        ### TODO: signals
        self.status_label = qw.QLabel()
        self.lang_label = qw.QLabel()
        self.statusBar().addWidget(self.status_label)
        self.statusBar().addWidget(self.lang_label)
        # Setting the result table
        ### TODO: signals
        self.predict_table = PredictTableWidget(self)
        layout.addWidget(self.predict_table, 3, 0, 3, 6)
        # Setting the toolbar
        ### TODO: signals
        self.toolbar = ToolBarWidget(self)
        self.addToolBar(self.toolbar)
        # Setting the console widget
        ### TODO: signals
        self.console = ConsoleWidget(self)
        layout.addWidget(self.console, 3, 6, 3, 2)
        # Lets play with fonts!
        self.setFont(QFont(self.font_family))

    def createMenu(self):
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

    ### TODO: signals in GUI class
    def set_font_size(self, size):
        """
        This slot changes the size of the window font.
        :param size:
        """
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    a = QApplication(sys.argv)
    m = MainWindow({"lang": ["ru", "en"], "rubr_id": ["tfidf"]})
    m.show()
    a.exec()
