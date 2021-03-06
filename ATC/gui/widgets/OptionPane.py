import PyQt5.QtWidgets as qw
from PyQt5.QtCore import pyqtSignal


class OptionPane(qw.QGroupBox):
    state_changed = pyqtSignal()
    display_option_changed = pyqtSignal(dict)

    section = "AvailableOptions"

    def __init__(self, config, clf_metadata, parent=None):
        super().__init__("Параметры", parent=parent)
        # Setting up form layout for parameter specifying
        layout = qw.QFormLayout()
        self.setLayout(layout)
        self.clf_md = clf_metadata
        # Rubricator id
        # Имена рубрикаторов грузятся классификатором
        ids = {"_".join(model.split("_")[:-1]) for model in clf_metadata}
        ids = sorted(list(ids))
        self.id_selector = qw.QComboBox(self)
        self.id_selector.addItems(ids)
        self.id_selector.currentIndexChanged.connect(self.state_changed)
        layout.addRow("Идентификатор рубрикатора", self.id_selector)
        # Language
        self.lang_selector = qw.QComboBox(self)
        languages = config.get(self.section, "languages").split(", ")
        self.lang_selector.addItems(languages)
        if "auto" in languages:
            self.lang_selector.setCurrentIndex(languages.index("auto"))
        else:
            self.lang_selector.setCurrentIndex(0)
        self.lang_selector.currentIndexChanged.connect(self.state_changed)
        layout.addRow("Язык", self.lang_selector)
        # Threshold
        self.threshold = qw.QDoubleSpinBox(self)
        self.threshold.setValue(0.0)
        self.threshold.setDecimals(5)
        self.threshold.setSingleStep(0.00005)
        self.threshold.setMaximum(1.0)
        self.threshold.valueChanged.connect(self.on_display_option_changed)
        layout.addRow("Порог вероятности", self.threshold)
        # Format
        self.format = qw.QComboBox(self)
        formats = config.get(self.section, "formats").split(", ")
        self.format.addItems(formats)
        if "auto" in formats:
            self.format.setCurrentIndex(formats.index("auto"))
        else:
            self.format.setCurrentIndex(0)
        self.format.currentIndexChanged.connect(self.state_changed)
        layout.addRow("Формат", self.format)
        # Normalization
        norm_options = config.get(self.section, "norm_predict").split(", ")
        self.normalization = qw.QComboBox(self)
        self.norm_mapping = {
            "not": "нет",
            "some": "да (если сумма > 1)",
            "all": "да (для всех)",
        }
        self.normalization.addItems([self.norm_mapping[i] for i in norm_options])
        self.normalization.currentIndexChanged.connect(self.on_display_option_changed)
        layout.addRow("Нормализация", self.normalization)
        # Code description
        self.description = qw.QCheckBox()
        self.description.setChecked(False)
        self.description.setMinimumSize(0, 50)
        self.description.stateChanged.connect(self.on_display_option_changed)
        layout.addRow("Расшифровка кодов", self.description)

    def on_display_option_changed(self):
        self.display_option_changed.emit(self.options_to_dict())

    def norm_dict_lookup(self, value):
        for k, v in self.norm_mapping.items():
            if v == value:
                return k
        raise ValueError(value)

    def options_to_dict(self):
        norm_text = self.normalization.currentText()
        inner_norm_val = self.norm_dict_lookup(norm_text)
        res = {
            "rubricator_id": self.id_selector.currentText(),
            "language": self.lang_selector.currentText(),
            "threshold": self.threshold.value(),
            "format": self.format.currentText(),
            "topic_names_allowed": self.is_description_allowed(),
            "normalize": inner_norm_val,
        }
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
