import PyQt5.QtWidgets as qw
from PyQt5.QtCore import pyqtSignal

###
### TODO: refactor
###


class OptionPane(qw.QGroupBox):

    state_changed = pyqtSignal()
    threshold_changed = pyqtSignal(float)
    description_state_changed = pyqtSignal(int)

    section = "AvailableOptions"

    def __init__(self, config, parent=None):
        super().__init__("Параметры", parent=parent)
        # Setting up form layout for parameter specifying
        layout = qw.QFormLayout()
        self.setLayout(layout)
        # Rubricator id
        self.id_selector = qw.QComboBox(self)
        self.id_selector.addItems(config.get(self.section, "ids").split(", "))
        self.id_selector.currentIndexChanged.connect(self.state_changed)
        layout.addRow("Идентификатор рубрикатора", self.id_selector)
        # Language
        self.lang_selector = qw.QComboBox(self)
        self.lang_selector.addItems(config.get(self.section, "languages").split(", "))
        self.lang_selector.setCurrentIndex(0)
        self.lang_selector.currentIndexChanged.connect(self.state_changed)
        layout.addRow("Язык", self.lang_selector)
        # Threshold
        self.threshold = qw.QDoubleSpinBox(self)
        self.threshold.setValue(0.0)
        self.threshold.setSingleStep(0.05)
        self.threshold.setMaximum(1.0)
        self.threshold.valueChanged.connect(self.threshold_changed)
        layout.addRow("Порог вероятности", self.threshold)
        # Code description
        self.description = qw.QCheckBox()
        self.description.setChecked(False)
        self.description.setMinimumSize(0, 50)
        self.description.stateChanged.connect(self.description_state_changed)
        layout.addRow("Расшифровка кодов", self.description)
        # Format
        self.format = qw.QComboBox(self)
        self.format.addItems(config.get(self.section, "formats").split(", "))
        self.format.setCurrentIndex(0)
        self.format.currentIndexChanged.connect(self.state_changed)
        layout.addRow("Формат", self.format)

    def options_to_dict(self):
        res = {}
        res["rubr_id"] = self.id_selector.currentText()
        res["language"] = self.lang_selector.currentText()
        res["threshold"] = self.threshold.value()
        res["format"] = self.format.currentText()
        return res

    def is_description_allowed(self):
        return self.description.isChecked()


# if __name__ == '__main__':
#     from PyQt5.QtWidgets import QApplication
#     import sys
#     from configparser import ConfigParser
#     c = ConfigParser()
#     c.read("../../config.ini")
#     a = QApplication(sys.argv)
#     m = OptionPane(c)
#     m.show()
#     a.exec()