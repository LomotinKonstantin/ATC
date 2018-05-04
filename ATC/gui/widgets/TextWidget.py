import PyQt5.QtWidgets as qw

###
### TODO: refactor, remove option pane
###


class TextWidget(qw.QTextEdit):

    def __init__(self, parent=None):
        super(TextWidget, self).__init__(parent)

    def insertFromMimeData(self, md):
        if not (md.hasText() or md.hasHtml()):
            return
        self.insertPlainText(md.text())

    def get_input(self):
        return self.toPlainText()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    a = QApplication(sys.argv)
    m = TextWidget()
    m.show()
    a.exec()


