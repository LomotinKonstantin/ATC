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
        # loading VINITI alphabet
        alph = open(".vocabulary/viniti_alphabet.txt").read().split("\n")
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
        #
