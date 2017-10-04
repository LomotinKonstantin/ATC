import PyQt5.QtWidgets as qw
from PyQt5.QtCore import pyqtSignal


class OptionBar(qw.QGroupBox):

    state_changed = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__("Параметры", parent=parent)
        # self.changed = True
        # setting up form layout for parameter specifying
        layout = qw.QFormLayout()
        self.setLayout(layout)
        # rubricator id
        self.id_selector = qw.QComboBox(self)
        self.id_selector.addItems(config.get(config.ID_OPTION))
        self.id_selector.currentIndexChanged.connect(self.state_changed)
        layout.addRow("Идентификатор рубрикатора", self.id_selector)
        # language
        self.lang_selector = qw.QComboBox(self)
        self.lang_selector.addItems(config.get(config.LANG_OPTION))
        self.lang_selector.currentIndexChanged.connect(self.state_changed)
        layout.addRow("Язык", self.lang_selector)
        # threshold
        self.threshold = qw.QDoubleSpinBox(self)
        self.threshold.setValue(0.0)
        self.threshold.setSingleStep(0.05)
        self.threshold.setMaximum(1.0)
        layout.addRow("Порог вероятности", self.threshold)
        # Description
        self.description = qw.QCheckBox()
        self.description.setChecked(False)
        self.description.setMinimumSize(0, 50)
        layout.addRow("Расшифровка кодов", self.description)

    def options_to_dict(self):
        res = {}
        res["rubricator_id"] = self.id_selector.currentText()
        res["language"] = self.lang_selector.currentText()
        res["threshold"] = self.threshold.value()
        return res

    # def on_changed(self):
    #     self.changed = True

    # def on_commited(self):
    #     self.changed = False

    def is_description_allowed(self):
        return self.description.isChecked()
