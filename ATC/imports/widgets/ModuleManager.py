import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

from collections import OrderedDict


class ModuleManager(qw.QDialog):

    module_changed = qc.pyqtSignal()

    def __init__(self, analyzer, config, parent=None):
        super().__init__(parent, flags=qc.Qt.WindowCloseButtonHint)
        self.analyzer = analyzer
        self.config = config
        self.setModal(True)
        self.setWindowTitle("Менеджер модулей")
        self.setMinimumSize(800, 400)
        self.changed = False

        # Layout
        layout = qw.QGridLayout()
        self.setLayout(layout)

        # Content
        self.tab_widget = qw.QTabWidget()
        self.tab_widget.tabBarClicked.connect(self.on_tab_clicked)
        layout.addWidget(self.tab_widget, 0, 0, 3, 2)

        # Buttons
        self.ok_button = qw.QPushButton("Ок")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.clicked.connect(self.update_modules)
        layout.addWidget(self.ok_button, 3, 2)
        self.cancel_button = qw.QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button, 3, 3)

        # Metadata widget
        groupbox = qw.QGroupBox("Информация")
        layout.addWidget(groupbox, 0, 2, 3, 2)
        self.metadata_widget = qw.QLabel()
        self.metadata_widget.setWordWrap(True)
        self.metadata_widget.setAlignment(qc.Qt.AlignTop)
        groupbox_layout = qw.QVBoxLayout()
        groupbox.setLayout(groupbox_layout)
        groupbox_layout.addWidget(self.metadata_widget)

        # Vectorizers tab
        self.vectorizers = qw.QListWidget()
        self.vectorizers.itemClicked.connect(self.on_item_clicked)
        self.available_vectorizers = self.analyzer.available_modules(self.analyzer.vectorizer_path,
                                                                     True)
        current_vector = self.config.get(self.config.WE_OPTION)
        for i in self.available_vectorizers.keys():
            j = qw.QListWidgetItem(i, self.vectorizers)
            if i == current_vector:
                j.setSelected(True)
        if len(self.available_vectorizers.keys()) == 1:
            self.vectorizers.item(0).setSelected(True)
        else:
            self.vectorizers.sortItems()
        self.tab_widget.addTab(self.vectorizers, "Векторайзеры")

        # Classifiers tab
        self.classifiers = qw.QListWidget()
        self.classifiers.itemClicked.connect(self.on_item_clicked)
        self.available_classifiers = self.analyzer.available_modules(self.analyzer.classifier_path,
                                                                     True)
        current_classifier = self.config.get(self.config.CLASSIFIER_OPTION)
        for i in self.available_classifiers.keys():
            j = qw.QListWidgetItem(i, self.classifiers)
            if i == current_classifier:
                j.setSelected(True)
        if len(self.available_classifiers.keys()) == 1:
            self.classifiers.item(0).setSelected(True)
        else:
            self.classifiers.sortItems()
        self.tab_widget.addTab(self.classifiers, "Классификаторы")
        # Initializing metadata widget
        self.on_tab_clicked(0)

    def on_tab_clicked(self, num):
        modules = self.tab_widget.widget(num)
        module = modules.selectedItems()
        if not module:
            self.metadata_widget.clear()
            return
        module_type = self.tab_num_to_available_modules(num)
        if module[0].text() in module_type.keys():
            self.display_metadata(module_type.get(module[0].text()))

    def display_metadata(self, metadata):
        if metadata:
            metastring = ""
            for key, value in metadata.items():
                metastring += "<b>{}</b>:  {}<br>".format(key, value)
        else:
            metastring = "<b>Информация о модуле недоступна!</b>"
        self.metadata_widget.setText(metastring)

    def on_item_clicked(self, item):
        num = self.tab_widget.currentIndex()
        module_type = self.tab_num_to_available_modules(num)
        if item.text() in module_type.keys():
            self.display_metadata(module_type.get(item.text()))

    def tab_num_to_available_modules(self, num):
        module_type = OrderedDict()
        if num == 1:
            module_type = self.available_vectorizers
        elif num == 2:
            module_type = self.available_classifiers
        return module_type

    def update_modules(self):
        self.changed = False
        vectorizer = self.tab_widget.widget(1)
        module = vectorizer.selectedItems()
        if module:
            old_vect = self.config.get(self.config.WE_OPTION)
            if old_vect != module[0].text():
                self.changed = True
                self.config.set(self.config.WE_OPTION, module[0].text())
        classifier = self.tab_widget.widget(2)
        module = classifier.selectedItems()
        if module:
            old_class = self.config.get(self.config.CLASSIFIER_OPTION)
            if old_class != module[0].text():
                self.changed = True
                self.config.set(self.config.CLASSIFIER_OPTION, module[0].text())
        if self.changed:
            self.module_changed.emit()
            self.config.save()
