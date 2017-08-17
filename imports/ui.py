import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
from PyQt5.QtGui import QIcon
import sys


class UI(qw.QMainWindow):

    def __init__(self, config):
        super().__init__()
        self.setMinimumSize(qc.QSize(800, 600))
        self.setWindowTitle("ATC: Automatic Text Classifier")
        self.setWindowIcon(QIcon("icon.ico"))
        # Setting up the layout
        layout = qw.QHBoxLayout(self)
        # opt_bar = OptionBar()
        # layout.addWidget(opt_bar)
        # Setting side option bar





    def launch(self):
        self.show()

if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    ui = UI()
    ui.launch()
    sys.exit(app.exec())
