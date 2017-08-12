import PyQt5.QtWidgets as qw

from imports.widgets.ControlWidget import ControlWidget
from imports.widgets.OptionBar import OptionBar


class MainWidget(qw.QWidget):

    def __init__(self, config, parent=None):
        super().__init__(parent)
        layout = qw.QGridLayout()
        self.setLayout(layout)
        # Widget with control buttons
        control = ControlWidget()
        layout.addWidget(control, 1, 1)
        # Setting side option bar
        opt_bar = OptionBar(config)
        layout.addWidget(opt_bar, 0, 1)