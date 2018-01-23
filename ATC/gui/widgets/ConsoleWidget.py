from PyQt5 import QtWidgets as qw

###
### TODO: implement console widget
###


class ConsoleWidget(qw.QTextEdit):

    def __init__(self, parent=None):
        super(ConsoleWidget, self).__init__(parent)
        self.setReadOnly(True)