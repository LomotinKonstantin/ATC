import re
import os

from pymystem3.mystem import Mystem
import pandas as pd

from modules.common import Module


class Preprocessor(Module):

    PLAIN = 0
    DIVIDED = 1
    MULTIDOC = 2
    UNKNOWN = 3
    MULTIDOC_COLUMS = ["id", "title", "body", "keywords", "correct"]
    DELIMITER = "┼┼┼"

    def __init__(self, lang, title_factor=1, text_factor=1, kw_factor=1):
        super().__init__(os.path.dirname(__file__) + "\\metadata.json")
        if not isinstance(lang, str):
            raise TypeError("Expected parameter lang of type str, got type " + str(type(lang)))
        self.title_factor = title_factor
        self.text_factor = text_factor
        self.kw_factor = kw_factor
        self.path = "./modules/preprocessor/preproc_v1/"
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

    def process_plain(self, text):
        """ Processes text. Removes all tokens except cyrillic and latin words.
            Lemmatization included

            Parameters
            ----------
            text: some text to process

            Returns
            -------
            pandas.DataFrame with cleared from VINITI`s alphabet and lemmatized text
        """
        s = text
        # Actually this check is not required
        # _Ё is already in service characters list and will be removed
        # if "_Ё" in s:
        #     s.remove("_Ё")
        s = s.lower()
        s = re.sub(self.email_re, "", s)
        # Removing VINITI alphabet
        for i in self.alphabet:
            s = s.replace(i, " ")
        s = re.sub("\s+", " ", s)
        s = re.sub(self.parse_re, "", s)
        # Lemmatization
        s = "".join(self.lemm.lemmatize(s))
        s = re.sub("(((?<=^)|(?<=\w))-+((?=\s)|(?=$)))|(((?<=^)|(?<=\s))-+((?=\w)|(?=\s)|(?=$)))", "", s)
        s = re.sub("(^|(?<=\s))\w{,2}(?=\s|$)", "", s)
        res_str = " ".join(list(filter(lambda a: a != "", s.split())))
        return pd.DataFrame([res_str], columns=["text"])

    def process(self, text : str):
        """
        :param text:
        :return: pandas.DataFrame with either ['id', 'text'] or ['text'] columns
        """
        if not text:
            return ""
        text_format = self.recognize_format(text)
        result = ""
        # Plain & divided texts are processed the same way
        if text_format == self.PLAIN or text_format == self.DIVIDED:
            result = self.process_plain(text)
        elif text_format == self.MULTIDOC:
            df_to_process = self.csv_to_df(text)
            rows_list = []
            for i in df_to_process.index:
                rows_list.append(" ".join([
                    df_to_process.loc[i, "title"] * self.title_factor,
                    df_to_process.loc[i, "body"] * self.text_factor,
                    df_to_process.loc[i, "keywords"] * self.kw_factor
                ]))
            str_repr = self.DELIMITER.join(rows_list)
            result_text = self.process_plain(str_repr).text.values[0]
            result_list = result_text.split(self.DELIMITER)
            result = pd.DataFrame(result_list, index=df_to_process.index, columns=["text"])
        return result

    def csv_to_df(self, text : str, delim="\t"):
        rows = text.splitlines(False)
        columns = rows[0].split(delim)
        data = [i for i in [j.split(delim) for j in rows[1:]]]
        result = pd.DataFrame(data, columns=columns)
        return result.set_index("id")

    def recognize_format(self, text : str):
        if re.match("((^|\t)[^\t]+){4,5}", text):
            return self.MULTIDOC
        if re.match("((^|\t)[^\t]+){3,}", text):
            return self.DIVIDED
        if re.match("(\w+?[^\t]+)+", text):
            return self.PLAIN
        return self.UNKNOWN


# if __name__ == '__main__':
#     from time import time
#     t = time()
#     a = Preprocessor("ru")
#     # # plain
#     # print(a.recognizeFormat(open("D:\\Desktop\\VINITI\\test_samples\\J15078903131.txt").read()))
#     # # divided
#     # print(a.recognizeFormat(open("D:\\Desktop\\VINITI\\test_samples\\J1500957X107.csv").read()))
#     # multidoc
#     text = open("D:\\Desktop\\VINITI\\test_samples\\multidoc.txt").read()
#     print(a.process(text).head())
#     print(time() - t, "секунд")
