from configparser import ConfigParser


class Config(object):
    def __init__(self, filename="./config.ini"):
        self._filename = filename
        self._section = "Settings"
        self._delimiter = ", "
        # Initialising config options
        self.ID_OPTION = "available_ids"
        self.PREPROC_OPTION = "preprocessor_import"
        self.WE_OPTION = "we_import"
        self.CLASSIFIER_OPTION = "classifier_import"
        self.FORMAT_OPTION = "available_formats"
        self.LANG_OPTION = "available_languages"
        self.options = {
            self.ID_OPTION : ["SUBJ", "IPV"],
            self.PREPROC_OPTION : "",
            self.WE_OPTION : "",
            self.CLASSIFIER_OPTION : "",
            self.FORMAT_OPTION : ["plain", "divided"],
            self.LANG_OPTION : ["ru"]
        }

    def save(self):
        """
        Saves current params to specified file
        :return: None
        """
        cfg_parser = ConfigParser()
        cfg_parser.add_section(self._section)
        for name, value in self.options.items():
            if isinstance(value, list):
                str_val = self._delimiter.join(value)
            else:
                str_val = value
            cfg_parser.set(self._section, name, str_val)
        with open(self._filename, "w") as config:
            cfg_parser.write(config)

    def load(self):
        parser = ConfigParser()
        parser.read(self._filename)
        for name, str_value in dict(parser.items(self._section)).items():
            # If the value is the list
            if self._delimiter in str_value:
                value = str_value.split(self._delimiter)
            else:
                value = str_value
            self.options[name] = value
        # Checking options that have to be list type,
        # but initially have only one value
        if not isinstance(self.options[self.LANG_OPTION], list):
            self.options[self.LANG_OPTION] = [self.options[self.LANG_OPTION]]

    def get(self, option):
        return self.options[option]

    def set(self, option, value):
        self.options[option] = value