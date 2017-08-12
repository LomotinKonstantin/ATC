import PyQt5.QtWidgets as qw
import sys

from ATC import ATC


class OptionBar(qw.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        # setting up form layout for parameter specifying
        layout = qw.QFormLayout(self)
        self.setLayout(layout)
        # rubricator id
        id_selector = qw.QComboBox(self)
        id_selector.addItems(ATC.config.get(ATC.config.ID_OPTION))
        layout.addRow("Идентификатор рубрикатора", id_selector)
        # language
        lang_selector = qw.QComboBox(self)
        lang_selector.addItems(ATC.config.get(ATC.config.LANG_OPTION))
        layout.addRow("Язык", lang_selector)
        # format
        format_selector = qw.QComboBox(self)
        format_selector.addItems(ATC.config.get(ATC.config.FORMAT_OPTION))
        layout.addRow("Формат", format_selector)
        # threshold
        threshold = qw.QDoubleSpinBox(self)
        threshold.setValue(0.0)
        threshold.setSingleStep(0.05)
        threshold.setMaximum(1.0)
        layout.addRow("Порог вероятности", threshold)

# if __name__ == "__main__":
#     app = qw.QApplication(sys.argv)
#     a = OptionBar()
#     a.show()
#     sys.exit(app.exec())
