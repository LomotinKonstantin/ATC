import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg

from imports.widgets.OptionBar import OptionBar
from imports.widgets.TextWidget import TextWidget


class MainWidget(qw.QWidget):

    def __init__(self, config, parent=None):
        super().__init__(parent)
        layout = qw.QHBoxLayout()
        self.setLayout(layout)
        # Setting text widget
        text_widget = TextWidget()
        layout.addWidget(text_widget)
        # Setting side option bar
        opt_bar = OptionBar(config)
        layout.addWidget(opt_bar)
        # Lets play with fonts!
        self.font_size = 12
        font = self.font()
        font.setPointSize(self.font_size)
        self.setFont(font)