import PyQt5.QtWidgets as qw
from PyQt5.Qt import QFont, QIcon
from PyQt5.QtCore import pyqtSignal

from gui.widgets.OptionPane import OptionPane
from gui.widgets.TextWidget import TextWidget
from gui.widgets.ResultWidget import ResultWidget
from gui.widgets.ToolBar import ToolBarWidget
from gui.widgets.ConsoleWidget import ConsoleWidget

###
### TODO: make this class the main widget inherited from QMainWindow
###


class MainWindow(qw.QMainWindow):
    font_family = "Segoe"
    font_size_selected = pyqtSignal()
    error_occurred = pyqtSignal(str)
    analyze_request = pyqtSignal()

    def __init__(self, config, parent=None):
        super(MainWindow, self).__init__(parent)
        self.config = config
        central_widget = qw.QWidget(self)
        # File dialogs
        self.load_dialog = qw.QFileDialog()
        self.save_dialog = qw.QFileDialog()
        # Setting the layout
        layout = qw.QGridLayout()
        central_widget.setLayout(layout)
        # Setting the side option bar
        self.opt_bar = OptionPane(config, parent=self)
        layout.addWidget(self.opt_bar, 0, 6, 4, 2)
        # Setting the text widget
        self.text_widget = TextWidget()
        layout.addWidget(self.text_widget, 0, 0, 3, 6)
        # Setting the toolbar
        ### TODO: signals
        self.toolbar = ToolBarWidget(self)
        self.addToolBar(self.toolbar)
        self.toolbar.open_action.triggered.connect(self.load_file)
        self.toolbar.analyze_action.connect()
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
        self.predict_widget = ResultWidget()
        layout.addWidget(self.predict_widget, 3, 0, 3, 6)
        # Setting the console widget
        ### TODO: signals
        self.console = ConsoleWidget()
        layout.addWidget(self.console, 4, 6, 2, 2)
        self.error_occurred.connect(self.console.printErrorMessage)
        # Lets play with fonts!
        self.setFont(QFont(self.font_family))
        #
        self.setCentralWidget(central_widget)

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
            # if i == self.font_size:
            #     action.setChecked(True)
            action.setActionGroup(group)
            font_menu.addAction(action)
            action.triggered.connect(self.font_size_selected)

    def set_font_size(self, size):
        """
        This slot changes the size of the window font.
        :param size: new font size
        """
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def load_file(self):
        filename = self.load_dialog.getOpenFileName()[0]
        if not filename:
            return
        try:
            content = open(file=filename).read()
            self.text_widget.setText(content)
        except Exception as e:
            self.error_occurred.emit("Не удалось прочитать текст из файла!")


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    from configparser import ConfigParser
    a = QApplication(sys.argv)
    c = ConfigParser()
    c.read("../../config.ini")
    m = MainWindow(c)
    m.showMaximized()
    a.exec()
