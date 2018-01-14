import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

###
### TODO: total refactoring
###


class LoadingWidget(qw.QProgressDialog):

    loaded = qc.pyqtSignal()

    def __init__(self, a=0, b=100, parent=None):
        super().__init__("", None, a, b, parent)
        self.setModal(True)
        self.setWindowFlags(qc.Qt.FramelessWindowHint | qc.Qt.WindowStaysOnTopHint)
        self.setMinimumDuration(0)

    def update_state(self, percentage : int, message : str):
        self.setValue(percentage)
        self.setLabelText(message)

# if __name__ == '__main__':
#     import sys
#     app = qw.QApplication(sys.argv)
#     m = int(1e5)
#     a = LoadingWidget(0, m)
#     a.show()
#     a.setAutoReset(False)
#     for i in range(m):
#         a.setValue(i)
#         a.setLabelText(str(i))
#     a.accept()
#     sys.exit(app.exec())