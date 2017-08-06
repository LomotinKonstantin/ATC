from configparser import ConfigParser


class Config(object):
    def __init__(self, filename="./config.ini"):
        self._filename = filename
        self._section = "Settings"
        self._delimiter = ", "
        # Initialising config options
        self.options = {
            "available_ids" : ["SUBJ", "IPV", "GRNTI", "RV"],
            "preprocessor" : "",
            "we_import" : "",
            "classifier_import" : ""
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
            if self._delimiter in str_value:
                value = str_value.split(self._delimiter)
            else:
                value = str_value
            self.options[name] = value

    def get(self, option):
        return self.options[option]

    def set(self, option, value):
        self.options[option] = value