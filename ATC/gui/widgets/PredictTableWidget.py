from PyQt5 import QtWidgets as qw
###
### TODO: implement PredictTableWidget inherited from QTableView
###


class PredictTableWidget(qw.QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
