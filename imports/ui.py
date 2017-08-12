import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
from PyQt5.QtGui import QIcon

from imports.widgets.MainWidget import MainWidget
from imports.widgets.ControlWidget import ControlWidget


class UI(qw.QMainWindow):

    def __init__(self, config):
        super().__init__()
        self.setMinimumSize(qc.QSize(800, 600))
        self.setWindowTitle("ATC: Automatic Text Classifier")
        self.setWindowIcon(QIcon("icon.ico"))
        # Toolbar
        toolbar = ControlWidget()
        self.addToolBar(toolbar)
        self.setCentralWidget(MainWidget(config))



    def launch(self):
        self.show()


# from ATC import ATC
# if __name__ == "__main__":
#     app = qw.QApplication(sys.argv)
#     ui = UI(ATC.config)
#     ui.launch()
#     sys.exit(app.exec())
