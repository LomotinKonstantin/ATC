import PyQt5.QtWidgets as qw

from imports.widgets.OptionBar import OptionBar


class MainWidget(qw.QWidget):

    def __init__(self, config, parent=None):
        super().__init__(parent)
        layout = qw.QVBoxLayout()
        self.setLayout(layout)
        # Setting side option bar
        opt_bar = OptionBar(config)
        layout.addWidget(opt_bar)