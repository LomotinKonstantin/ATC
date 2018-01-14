import PyQt5.QtWidgets as qw

from imports.widgets.OptionBar import OptionBar
from imports.widgets.TextWidget import TextWidget

###
### TODO: make this class the main widget inherited from QMainWindow
###


class MainWidget(qw.QWidget):

    def __init__(self, config, parent=None):
        super().__init__(parent)
        layout = qw.QHBoxLayout()
        self.setLayout(layout)
        # Setting side option bar
        self.opt_bar = OptionBar(config)
        # Setting text widget
        self.text_widget = TextWidget(self.opt_bar)
        layout.addWidget(self.text_widget)
        layout.addWidget(self.opt_bar)
        # Lets play with fonts!
        self.font_size = 12
        self.set_font_size(self.font_size)

    def set_font_size(self, size):
        font = self.font()
        self.font_size = size
        font.setPointSize(size)
        self.setFont(font)
