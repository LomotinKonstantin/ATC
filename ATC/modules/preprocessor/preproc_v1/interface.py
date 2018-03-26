import os
import re
from random import choice

import pandas as pd
from pymystem3.mystem import Mystem
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer

from modules.common import Module


def expand_language(lang: str):
    if lang == "ru":
        return "russian"
    if lang == "en":
        return "english"


class Normalizer:
    def __init__(self, norm: str, language: str):
        self.norm = norm
        self.language = language

    def normalize(self, text: str, return_list=False):
        res = None
        token_list = None
        # Лемматизация
        if self.norm == "lemmatization":
            # PyMystem3 не поддерживает английский
            # NLTK.WordNetLemmatizer не поддерживает русский
            if self.language == "ru":
                alg = Mystem()
                token_list = alg.lemmatize(text)
            elif self.language == "en":
                alg = WordNetLemmatizer()
                token_list = list(map(alg.lemmatize, text.split()))
        # Стемминг
        elif self.norm == "stemming":
            alg = SnowballStemmer(expand_language(self.language))
            token_list = list(map(alg.stem, text.split()))
        else:
            raise ValueError("{} is not supported. "
                             "Available options: 'lemmatization, 'stemming'".format(self.norm))
        # Выбор формата результата
        if not return_list:
            res = " ".join(remove_empty_items(token_list))
        else:
            res = token_list
        return res


def remove_empty_items(lst):
    return list(filter(lambda x: not bool(re.fullmatch("\s*", x)), lst))


class Preprocessor(Module):
    """
    Класс для выполнения предобработки однотипных данных.
    Может брать данные из двух уровней источников:
        - Обычный текст:    метод preprocess(text: str)
        - Если данные нуждаются в дополнительной обработке до препроцессинга,
          можно обработать DataFrame: метод preprocess_dataframe(texts: DataFrame)
    """

    delim = " ☺☻ "
    sw_files = {"ru": "ru_stopwords.txt",
                "en": "en_stopwords.txt"}
    md_file = "viniti_md.txt"

    MULTIDOC = 0
    DIVIDED = 1
    PLAIN = 2
    UNKNOWN = 3
    MULTIDOC_COLUMNS = ("id", "title", "body", "keywords", "correct")

    def __init__(self, groups_to_save=("буквы рус.", "пробел", "дефис", "буквы лат."),
                 title_factor=1, body_factor=1, kw_factor=1):
        """
        Препроцессор для обработки обучающих данных из ВИНИТИ.
        ---------------------------------------------------
        Аргументы:

            groups_to_save: Группы символов алфавита ВИНИТИ, которые не будут удалены из текста
                "буквы рус."       - кириллица (сохр. по умолчанию)
                "буквы греч."      - буквы греческого алфавита
                "буквы лат."       - латинские буквы (сохр. по умолчанию)
                "буквы спец."      - буквы љ, њ (хорватский), готические и ажурные буквы (использ. в математике)
                "дефис"            - в этой группе только дефис "-" (сохр. по умолчанию)
                "диакриты"         - диакритические символы (á, ŝ, ž и т.д.)
                "диакр. наезж."    - другие диакриты
                "зн. преп. обычн." - знаки препинания.
                "индексы"          - обозначения верхних и нижних индексов
                "команды"          - перевод, начало и конец строки, жирный шрифт, курсив, цвет
                "пробел            - в этой группе только пробел " "
                "служебные"        - признак текста с посторонней разметкой и нераспознанного символа, приоритеты при сортировке
                "спец. зн. доп."   - тильда, валюта, градус, планеты, обратный слэш
                "стрелки"          - разные стрелки ascii
                "точка"            - в этой группе только точка "."
                "форм. доп."       - математические символы, операторы и константы
                "форм. обычн."     - арифметические операторы
                "цифры"            - арабские цифры
        """

        super().__init__(os.path.join(os.path.dirname(__file__), "metadata.json"))
        self.groups_to_save = groups_to_save
        self.title_factor = title_factor
        self.body_factor = body_factor
        self.kw_factor = kw_factor
        self.normalizer = None
        self.path = "./modules/preprocessor/preproc_v1/"
        for lang, fn in self.sw_files.items():
            self.sw_files[lang] = os.path.join(os.path.dirname(__file__),
                                               "vocabulary",
                                               self.sw_files[lang])
        self.stopwords = self.__load_sw()
        self.viniti_md = self.__load_md()
        self.DEBUG = False

    def __dense(self, text: str) -> str:
        return re.sub("\\s{2,}", " ", text)

    def __remove_stopwords(self, text: str, lang: str) -> str:
        return " ".join(filter(lambda x: x not in self.stopwords[lang], text.split()))

    def __remove_double_formulas(self, text: str, sub=" ") -> str:
        return re.sub("\\${2}(?!\\$).+?\\${2}", sub, text)

    def __remove_currency(self, text: str) -> str:
        return re.sub("(?<=[^$])\\$\\d+(,\\d+)?", " ", text)

    def __remove_single_formulas(self, text: str, sub=" ") -> str:
        return re.sub("(?<=[\\sЁё])\\$(?=[^$\\s]).+?(?<=[^$])\\$", sub, text)

    def __remove_email(self, text: str, sub=" ") -> str:
        return re.sub("[\\w./-]+@[\\w./-]*\\.\\w+", sub, text)

    def __remove_md(self, text: str) -> str:
        res = text
        for i in self.viniti_md:
            res = res.replace(i, " ")
        return res

    def __beautify(self, text: str) -> str:
        # Fix -blablabla-
        res = re.sub("(?<!\\S)\\S(?=\\s|$)", " ", text)
        # Fix blabla - a f - g blablabla
        res = re.sub("(\\b-\\B)|(\\B-\\b)", " ", res)
        # Fix blabla ~--_ -- ___ bla !!! blabla
        res = re.sub("(?<=\\s)[!~+@#$%^&*_-]+?(?=\\s)", " ", res)
        return self.__dense(res).strip()

    def __load_md(self) -> tuple:
        md_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                         "vocabulary",
                                         "viniti_md.txt"),
                            encoding="cp1251",
                            sep="\t",
                            names=["element", "meaning", "code", "group"],
                            quoting=3)
        md_df.drop(md_df.index[md_df.group.isin(self.groups_to_save)], inplace=True)
        return tuple(sorted(md_df.element, key=lambda x: len(x), reverse=True))

    def __load_sw(self) -> dict:
        res = {}
        for lang, fn in self.sw_files.items():
            file = open(os.path.join(".", fn), encoding="utf8")
            sw = file.read().split()
            res[lang] = tuple(remove_empty_items(sw))
        return res

    def __csv_to_df(self, text: str, delim="\t"):
        rows = text.splitlines(keepends=False)
        first_row = rows[0].split(delim)
        if tuple(first_row) == self.MULTIDOC_COLUMNS:
            index = 1
        else:
            index = 0
        data = [i for i in [j.split(delim) for j in rows[index:]]]
        result = pd.DataFrame(data, columns=self.MULTIDOC_COLUMNS)
        return result.set_index("id")

    def recognize_language(self, text: str, default="none"):
        """
        Распознавание языка текста на основе предварительно загруженных стоп-слов.
        Если стоп-слова не загружены, нужно загрузить их:
            self.stopwords = self.__load_sw()
        -------------------------------------------------
        Аргументы:

            text: Текст, язык которого надо определить.

            default: Действия в случае несоответствия текста ни одному из языков.
                     Варианты:
                         - "random": Попробовать угадать язык случайным образом
                         - "error" : Вызвать ошибку
                         - "none"  : Вернуть None (default)
        """
        text_set = set(text.lower().split())
        res_lang = None
        max_entries = 0
        for lang, sw in self.stopwords.items():
            sw_set = set(sw)
            entries = len(text_set.intersection(sw_set))
            if entries > max_entries:
                max_entries = entries
                res_lang = lang
        if res_lang is None:
            if default == "random":
                res_lang = choice(tuple(self.stopwords.keys()))
            elif default == "error":
                raise ValueError("Не удалось определить язык")
        return res_lang

    def recognize_format(self, text: str):
        if "\n" in text.strip():
            return self.MULTIDOC
        if re.match("((^|\t)[^\t]+){3,}", text.strip()):
            return self.DIVIDED
        if re.match("(\w+?[^\t]+)+", text.strip()):
            return self.PLAIN
        return self.UNKNOWN

    def preprocess(self,
                   text: str,
                   remove_stopwords: bool,
                   normalization: str,
                   language="auto",
                   default_lang="error") -> str:
        """
        Предобработка одного текста.
        ----------------------------
        Аргументы:

            text: Строка с текстом для предобработки.

            remove_stopwords: Удалять стоп-слова.
                              Возможные варианты: [True, False].

            normalizaion: Метод нормализации слова. Возможные варианты:
                          ["no", "lemmatization", "stemming"].

            language: Язык текста. По умолчанию язык определяется автоматически.
                      Возможные варианты: ["auto", "ru", "en"].
                      Автоопределение занимает время (особенно на больших текстах),
                      поэтому лучше задать определенный язык.

            default_lang: Действия в случае несоответствия текста ни одному из языков.
                          Аргумент используется только при language="auto".
                          Варианты:
                             - "random": Попробовать угадать язык случайным образом
                             - "error" : Вызвать ошибку
                             - "none"  : Вернуть None (default)
        """
        lang = language
        if language == "auto":
            lang = self.recognize_language(text.lower(), default_lang)
        res = self.__remove_email(text)
        # Fix _ёvar blabla _ёEpsilon bla
        res = re.sub("\\w*_ё\\w+", " ", res)
        res = self.__remove_md(res)
        res = res.replace("ё", "е")
        if remove_stopwords:
            res = self.__dense(res)
            res = self.__remove_stopwords(res.lower(), lang)
        res = self.__beautify(res)
        if normalization != "no":
            res = Normalizer(normalization, lang).normalize(res)
        res = re.sub("\\s-\\s", "-", res)
        res = self.__beautify(res)
        return res

    def process(self, text, lang="auto"):
        if not text:
            return ""
        if lang == "auto":
            language = self.recognize_language(text)
        else:
            language = lang
        text_format = self.recognize_format(text)
        result = ""
        # Plain & divided texts are processed the same way
        try:
            if text_format in [self.PLAIN, self.DIVIDED, self.UNKNOWN]:
                processed_text = self.preprocess(text=text,
                                         remove_stopwords=True,
                                         normalization="lemmatization",
                                         language=language)
                result = pd.DataFrame([processed_text], columns=["text"])
            elif text_format == self.MULTIDOC:
                df_to_process = self.__csv_to_df(text)
                self.debug(df_to_process)
                rows_list = []
                for i in df_to_process.index:
                    rows_list.append(" ".join([
                        df_to_process.loc[i, "title"] * self.title_factor,
                        df_to_process.loc[i, "body"] * self.body_factor,
                        df_to_process.loc[i, "keywords"] * self.kw_factor
                    ]))
                # Delimiter is wrapped in spaces
                str_repr = self.delim.join(rows_list)
                result_text = self.preprocess(text=str_repr,
                                              remove_stopwords=True,
                                              normalization="lemmatization",
                                              language=language)
                result_list = result_text.split(self.delim)
                result = pd.DataFrame(result_list, index=df_to_process.index, columns=["text"])
        except Exception as e:
            self.debug(e)
            self.error_occurred.emit("Не удается обработать текст")
            result = pd.DataFrame([""], columns=["text"])
        return result