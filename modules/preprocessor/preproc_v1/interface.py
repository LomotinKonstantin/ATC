import re
import os

from pymystem3.mystem import Mystem
import pandas as pd

from modules.common import Module


class Preprocessor(Module):

    def __init__(self, format, lang):
        super().__init__()
        if not isinstance(format, str):
            raise TypeError("Expected parameter 'format' of type str, got type " + str(type(format)))
        if not isinstance(lang, str):
            raise TypeError("Expected parameter lang of type str, got type " + str(type(lang)))
        self.path = "./modules/preprocessor/preproc_v1/"
        self.format = format
        self.lang = lang
        self._load_vocabulary()
        self.email_re = "(^|(?<=\s))([\w._-]+@[a-zA-Z]+\.\w+)(?=\s|$)"
        self.lemm = Mystem()
        pac_str = ("(" + ")|(".join(self.stop_words) + ")" + "|(\w{,2})")
        self.parse_re = re.compile("(^|(?<=\s))(" + pac_str + ")(?=\s|$)")

    def _load_vocabulary(self):
        # Loading VINITI alphabet
        alph = open(os.path.dirname(__file__) + "/vocabulary/viniti_alphabet.txt").read().split("\n")
        alph = list(filter(lambda a: a != "", alph))
        rules = {}
        for i in alph:
            comp = i.split("\t")
            if comp[-1] not in rules.keys():
                rules[comp[-1]] = [comp[0]]
            else:
                rules[comp[-1]].append(comp[0])
        for i in rules:
            rules[i] = [rules[i]]
        alph_df = pd.DataFrame(rules)
        alph_df.drop(["буквы рус.",
                      "пробел",
                      "дефис",
                      "буквы лат."], axis=1, inplace=True)
        # TODO add smth to keep
        # alph_df.drop(["диакриты",
        #               "буквы спец.",
        #               "буквы греч.",
        #               "форм. доп.",
        #               "диакр. наезж."], axis=1, inplace=True)
        self.alphabet = [i for j in alph_df.values.flatten() for i in j]
        # Loading stop-words
        self.stop_words = open(os.path.dirname(__file__) + "/vocabulary/stop_words.txt", encoding="utf-8").read().split("\n")
        self.stop_words = list(filter(lambda a: a != "", self.stop_words))

    def process(self, text):
        """ Processes text. Removes all tokens except cyrillic and latin words. Lemmatization included

            Parameters
            ----------
            text: some text to process

            Returns
            -------
            Clear from VINITI`s alphabet and lemmatized text
        """
        s = text
        # Definitely this check is not required
        # _Ё is already in service characters list and will be removed
        # if "_Ё" in s:
        #     s.remove("_Ё")
        s = s.lower()
        s = re.sub(self.email_re, "", s)
        # Removing VINITI alphabet
        for i in self.alphabet:
            s = s.replace(i, "")
        s = re.sub("\s+", " ", s)
        s = re.sub(self.parse_re, "", s)
        # Lemmatization
        s = "".join(self.lemm.lemmatize(s))
        s = re.sub("(((?<=^)|(?<=\w))-+((?=\s)|(?=$)))|(((?<=^)|(?<=\s))-+((?=\w)|(?=\s)|(?=$)))", "", s)
        s = re.sub("(^|(?<=\s))\w{,2}(?=\s|$)", "", s)
        res_str = " ".join(list(filter(lambda a: a != "", s.split())))
        return pd.DataFrame(data=[res_str], columns=["text"])
