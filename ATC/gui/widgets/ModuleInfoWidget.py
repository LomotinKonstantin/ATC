import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from collections import OrderedDict

###
### TODO: change the widget totally according to the new functionality
###


def get_env() -> dict:
    """
    Получает список установленных модулей и их версии
    :return: Словарь вида {модуль: версия} или пустой словарь, если не удалось
    """
    try:
        from pkg_resources import working_set
        return {i.key: i.version for i in working_set}
    except ImportError:
        return {}


class ModuleInfoWidget(qw.QDialog):

    module_changed = qc.pyqtSignal()

    def __init__(self, analyzer, parent=None):
        super().__init__(parent, flags=qc.Qt.WindowCloseButtonHint)
        self.analyzer = analyzer
        self.setModal(True)
        self.setWindowTitle("О программе")
        self.setMinimumSize(800, 400)
        # Layout
        layout = qw.QGridLayout()
        self.setLayout(layout)
        # Content
        self.tab_widget = qw.QTabWidget()
        layout.addWidget(self.tab_widget, 0, 0, 3, 5)
        # Buttons
        self.cancel_button = qw.QPushButton("Закрыть")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button, 3, 4)
        self.copy_button = qw.QPushButton("Копировать")
        self.copy_button.clicked.connect(self.module_info_to_cb)
        self.copy_button.setHidden(True)
        layout.addWidget(self.copy_button, 3, 0)
        # Preprocessors tab
        self.preprocessor_mdw = self.createMetadataWidget()
        preprocessor_metadata = analyzer.preprocessor.metadata
        self.preprocessor_mdw.setText(self.md_dict_to_html(preprocessor_metadata))
        self.tab_widget.addTab(self.preprocessor_mdw, "Предобработчик")
        # Vectorizers tab
        self.vectorizer_mdw = self.createMetadataWidget()
        vectorizer_metadata = analyzer.vectorizer.metadata
        self.vectorizer_mdw.setText(self.md_dict_to_html(vectorizer_metadata))
        self.tab_widget.addTab(self.vectorizer_mdw, "Векторизатор")
        # Classifiers tab
        self.classifier_mdw = self.createMetadataWidget()
        classifier_metadata = analyzer.classifier.metadata
        self.classifier_mdw.setText(self.md_dict_to_html(classifier_metadata))
        self.tab_widget.addTab(self.classifier_mdw, "Классификатор")
        # Environment tab
        self.module_info = get_env()
        if not self.module_info:
            self.environment_widget = self.createMetadataWidget()
            self.environment_widget.setText(
                "<b>Не удалось загрузить список установленных пакетов</b>"
            )
        else:
            table = qw.QTableWidget()
            table.setRowCount(len(self.module_info.keys()))
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Модуль", "Версия"])
            for n, (module, version) in enumerate(self.module_info.items()):
                table.setItem(n, 0, qw.QTableWidgetItem(module))
                table.setItem(n, 1, qw.QTableWidgetItem(version))
            table.resizeColumnsToContents()
            table.horizontalHeader().setSectionResizeMode(qw.QHeaderView.Fixed)
            table.verticalHeader().setSectionResizeMode(qw.QHeaderView.Fixed)
            self.environment_widget = table
        self.tab_widget.addTab(self.environment_widget, "Пакеты")
        self.tab_widget.currentChanged.connect(self.on_tab_clicked)
        # Initializing metadata widget
        # self.on_tab_clicked(0)

    def createMetadataWidget(self) -> qw.QLabel:
        metadata_widget = qw.QLabel()
        metadata_widget.setWordWrap(True)
        metadata_widget.setAlignment(qc.Qt.AlignTop)
        return metadata_widget

    def md_dict_to_html(self, metadata: OrderedDict) -> str:
        if metadata:
            metastring = ""
            for key, value in metadata.items():
                metastring += "<b>{}</b>:  {}<br>".format(key, value)
        else:
            metastring = "<b>Информация о модуле недоступна!</b>"
        return metastring

    def module_info_to_cb(self):
        text_repr = "\n".join([f"{module}: {version}" for module, version in self.module_info.items()])
        qw.QApplication.instance().clipboard().setText(text_repr)

    def on_tab_clicked(self, num):
        tab = self.tab_widget.widget(num)
        if tab == self.environment_widget:
            self.copy_button.setHidden(False)
        else:
            self.copy_button.setHidden(True)
