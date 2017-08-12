import re

from pymystem3.mystem import Mystem
import pandas as pd

from modules.common import Module


class Preprocessor(Module):

    def __init__(self, rubr_id, lang):
        super().__init__()
        if not isinstance(rubr_id, str):
            raise TypeError("Expected parameter rubr_id of type str, got type " + str(type(rubr_id)))
        if not isinstance(lang, str):
            raise TypeError("Expected parameter lang of type str, got type " + str(type(lang)))
        self.rubr_id = rubr_id
        self.lang = lang
        self._load_vocabulary()

    def _load_vocabulary(self):
        # Loading VINITI alphabet
        alph = open("./vocabulary/viniti_alphabet.txt").read().split("\n")
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
        self.stop_words = open(".vocabulary/stop_words.txt", encoding="utf-8").read().split("\n")
        self.stop_words = list(filter(lambda a: a != "", self.stop_words))

    def process(self, text):
        """ Processing some text. Removes tokens depending on 'mode' selected. Lemmatization included

            Parameters
            ----------
            text: some text to process

            Returns
            -------
            Clear from VINITI`s alphabet and lemmatized text

        """
        fin = "###"
        s = text.strip()
        if s.contains("_Ё"):
            s.remove("_Ё")
        s = s.lower()
        s = re.sub(self.email_re, "", s)
        for i in self.chars:
            s = s.replace(i, "")
        s = re.sub("\s+", " ", s)
        s = re.sub(self.parse_re, "", s)
        print("Lemmatization...")
        s = "".join(self.lemm.lemmatize(s))
        print("Removing redundant \"-\"")
        s = re.sub("(((?<=^)|(?<=\w))-+((?=\s)|(?=$)))|(((?<=^)|(?<=\s))-+((?=\w)|(?=\s)|(?=$)))", "", s)
        print("Removing remainings")
        s = re.sub("(^|(?<=\s))\w{,2}(?=\s|$)", "", s)
        return " ".join(list(filter(lambda a: a != "", s.split())))