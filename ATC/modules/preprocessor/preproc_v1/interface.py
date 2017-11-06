import re
import os

from pymystem3.mystem import Mystem
import pandas as pd
from nltk import WordNetLemmatizer, pos_tag, wordpunct_tokenize
from nltk.corpus import stopwords

from modules.common import Module


class Preprocessor(Module):

    PLAIN = 0
    DIVIDED = 1
    MULTIDOC = 2
    UNKNOWN = 3
    MULTIDOC_COLUMS = ["id", "title", "body", "keywords", "correct"]
    DELIMITER = "┼┼┼"

    def __init__(self, title_factor=1, text_factor=1, kw_factor=1):
        super().__init__(os.path.dirname(__file__) + "\\metadata.json")
        self.title_factor = title_factor
        self.text_factor = text_factor
        self.kw_factor = kw_factor
        self.path = "./modules/preprocessor/preproc_v1/"
        self._load_vocabulary()
        self.email_re = "(^|(?<=\s))([\w._-]+@[a-zA-Z]+\.\w+)(?=\s|$)"
        pac_str = ("(" + ")|(".join(self.stop_words) + ")" + "|(\w{,2})")
        self.parse_re = re.compile("\b(" + pac_str + ")\b")

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
        self.alphabet = [i for j in alph_df.values.flatten() for i in j]
        # Loading stop-words
        self.stop_words = open(os.path.dirname(__file__) + "/vocabulary/stop_words.txt",
                               encoding="utf-8").read().split("\n")
        self.stop_words = list(filter(lambda a: a != "", self.stop_words))

    def process_plain(self, text, lang):
        """ Processes text. Removes all tokens except cyrillic and latin words.
            Lemmatization included

            Parameters
            ----------
            text: some text to process

            Returns
            -------
            pandas.DataFrame with cleared from VINITI`s alphabet and lemmatized text
        """
        lemm = Lemmatizer(lang)
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
        # Reducing the diversity of possible spellings
        s = s.replace("ё", "е")
        s = re.sub("\s+", " ", s)
        # Regexp doesn't work for some reason, so
        # we use built-in python functions.
        # I hope, they are optimized
        s = " ".join(filter(lambda x : x not in self.stop_words, s.split()))
        # Lemmatization
        s = "".join(lemm.lemmatize(s))
        # Mmm... Let it be so
        s = re.sub("(((?<=^)|(?<=\w))-+((?=\s)|(?=$)))|(((?<=^)|(?<=\s))-+((?=\w)|(?=\s)|(?=$)))", "", s)
        # Removing all words shorter than 2 letters
        s = re.sub("\b\w{,2}\b", "", s)
        res_str = " ".join(list(filter(lambda a: a != "", s.split())))
        return pd.DataFrame([res_str], columns=["text"])

    def process(self, text: str, lang="auto"):
        """
        :param lang: Text language (default: auto)
        :param text: Text to turn into bag-of-words
        :return: tuple: (pandas.DataFrame with either ['id', 'text'] or ['text'] columns, language)
        """
        if not text:
            return ""
        if lang == "auto":
            language = self.recognize_language(text)[:2]
        else:
            language = lang
        text_format = self.recognize_format(text)
        result = ""
        # Plain & divided texts are processed the same way
        try:
            if text_format in [self.PLAIN, self.DIVIDED, self.UNKNOWN]:
                result = self.process_plain(text, language)
            elif text_format == self.MULTIDOC:
                df_to_process = self.csv_to_df(text)
                rows_list = []
                for i in df_to_process.index:
                    rows_list.append(" ".join([
                        df_to_process.loc[i, "title"] * self.title_factor,
                        df_to_process.loc[i, "body"] * self.text_factor,
                        df_to_process.loc[i, "keywords"] * self.kw_factor
                    ]))
                # A little magic in order to create space around the first word in
                # each text
                str_repr = (" " + self.DELIMITER + " ").join(rows_list)
                result_text = self.process_plain(str_repr, language).text.values[0]
                result_list = result_text.split(self.DELIMITER)
                result = pd.DataFrame(result_list, index=df_to_process.index, columns=["text"])
        except Exception as e:
            self.error_occurred.emit("Не удается обработать текст")
            result = pd.DataFrame([""], columns=["text"])
        return result, language

    def csv_to_df(self, text: str, delim="\t"):
        rows = text.splitlines(False)
        first_row = rows[0].split(delim)
        if first_row == self.MULTIDOC_COLUMS:
            index = 1
        else:
            index = 0
        data = [i for i in [j.split(delim) for j in rows[index:]]]
        result = pd.DataFrame(data, columns=self.MULTIDOC_COLUMS)
        return result.set_index("id")

    def recognize_format(self, text: str):
        if re.match("((^|\t)[^\t]+){4,5}", text):
            return self.MULTIDOC
        if re.match("((^|\t)[^\t]+){3,}", text):
            return self.DIVIDED
        if re.match("(\w+?[^\t]+)+", text):
            return self.PLAIN
        return self.UNKNOWN

    def recognize_language(self, text: str):
        languages_ratios = {}
        tokens = wordpunct_tokenize(text)
        words = [word.lower() for word in tokens]
        for language in stopwords.fileids():
            stopwords_set = set(stopwords.words(language))
            words_set = set(words)
            common_elements = words_set.intersection(stopwords_set)
            languages_ratios[language] = len(common_elements)
        most_rated_language = max(languages_ratios, key=languages_ratios.get)
        return most_rated_language


class Lemmatizer:

    pos_map = {
        "NN": "n",
        "JJ": "a",
        "VB": "v"
    }

    def __init__(self, lang: str):
        self.lang = lang
        if self.lang == "ru":
            self.lemmatize = Mystem().lemmatize
        elif self.lang == "en":
            self.lemmatize = self.nltk_lemmatize

    def nltk_lemmatize(self, text):
        tag = pos_tag([text])[0][1]
        lemm = WordNetLemmatizer()
        if tag in self.pos_map.keys():
            tag = self.pos_map[tag]
        else:
            tag = "v"
        res = []
        for word in text.split():
            res.append(lemm.lemmatize(word, tag))
        res = " ".join(res)
        return res