import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from collections import OrderedDict

###
### TODO: change the widget totally according to the new functionality
###


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

    # def on_tab_clicked(self, num):
    #     modules = self.tab_widget.widget(num)
    #     module = modules.selectedItems()
    #     if not module:
    #         self.metadata_widget.clear()
    #         return
    #     module_type = self.tab_num_to_available_modules(num)
    #     if module[0].text() in module_type.keys():
    #         self.display_metadata(module_type.get(module[0].text()))
