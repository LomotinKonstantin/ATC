import PyQt5.QtWidgets as qw


class OptionBar(qw.QWidget):

    def __init__(self, config, parent=None):
        super().__init__(parent)
        # setting up form layout for parameter specifying
        layout = qw.QFormLayout(self)
        self.setLayout(layout)
        # rubricator id
        id_selector = qw.QComboBox(self)
        id_selector.addItems(config.get(config.ID_OPTION))
        layout.addRow("Идентификатор рубрикатора", id_selector)
        # language
        lang_selector = qw.QComboBox(self)
        lang_selector.addItems(config.get(config.LANG_OPTION))
        layout.addRow("Язык", lang_selector)
        # format
        format_selector = qw.QComboBox(self)
        format_selector.addItems(config.get(config.FORMAT_OPTION))
        layout.addRow("Формат", format_selector)
        # threshold
        threshold = qw.QDoubleSpinBox(self)
        threshold.setValue(0.0)
        threshold.setSingleStep(0.05)
        threshold.setMaximum(1.0)
        layout.addRow("Порог вероятности", threshold)

# import sys
# from ATC import ATC
# if __name__ == "__main__":
#     app = qw.QApplication(sys.argv)
#     a = OptionBar(ATC.config)
#     a.show()
#     sys.exit(app.exec())
