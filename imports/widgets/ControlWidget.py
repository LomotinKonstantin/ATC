import PyQt5.QtWidgets as qw


class ControlWidget(qw.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = qw.QGridLayout()
        self.setLayout(layout)
        # Buttons
        start_button = qw.QPushButton("Анализировать")
        layout.addWidget(start_button, 0, 0, 1, 2)
        import_button = qw.QPushButton("Открыть файл")
        layout.addWidget(import_button, 1, 0)
        export_button = qw.QPushButton("Экспорт")
        layout.addWidget(export_button, 1, 1)


