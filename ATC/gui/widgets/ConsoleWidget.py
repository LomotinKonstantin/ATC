import datetime
from PyQt5 import QtWidgets as qw


class ConsoleWidget(qw.QTextEdit):
    gap = " "

    def __init__(self, parent=None, enable_time_stamps=True, hist_size=30):
        super(ConsoleWidget, self).__init__(parent)
        self.hist_size = hist_size
        self.content_list = []
        self.enable_ts = enable_time_stamps
        self.setReadOnly(True)

    def timeStamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def printErrorMessage(self, message):
        ts, gap = self.formattedTimeStampAndGap()
        self.updateView("{}{}<font color='red'><b>{}</b></font>".format(ts, gap, message))

    def printWarningMessage(self, message):
        ts, gap = self.formattedTimeStampAndGap()
        self.updateView("{}{}<font color='#ff9900'><b>{}</b></font>".format(ts, gap, message))

    def printInfoMessage(self, message):
        ts, gap = self.formattedTimeStampAndGap()
        self.updateView("{}{}{}".format(ts, gap, message))

    # def mousePressEvent(self, event):
    #     """
    #     Test function
    #     """
    #     if event.button() == qt.Qt.LeftButton:
    #         self.printInfoMessage("Что-то сделалось :3")
    #     elif event.button() == qt.Qt.MidButton:
    #         self.printWarningMessage("Что-то немного не так..." * 10)
    #     elif event.button() == qt.Qt.RightButton:
    #         self.printErrorMessage("Что-то совсем не так!")

    def formattedTimeStampAndGap(self):
        ts = ""
        gap = ""
        if self.enable_ts:
            ts = "<font color=#8a8a8a>{}</font>".format(self.timeStamp())
            gap = self.gap
        return ts, gap

    def contentListToString(self):
        return "<br>".join(self.content_list)

    def updateView(self, new_content):
        if len(self.content_list) == self.hist_size:
            del self.content_list[0]
        self.content_list.append(new_content)
        self.setHtml(self.contentListToString())
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


# if __name__ == '__main__':
#     from PyQt5.QtWidgets import QApplication
#     import sys
#
#     a = QApplication(sys.argv)
#     m = ConsoleWidget()
#     m.show()
#     a.exec()