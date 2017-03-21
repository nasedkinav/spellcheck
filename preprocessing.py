# coding: utf-8
import re
import nltk
import string
import pymorphy2

from n2t import numbers2letters


russian_vowels = ['а', 'у', 'о', 'ы', 'и', 'э', 'я', 'ю', 'ё', 'е']
russian_vowels_str = ''.join(russian_vowels)
russian_cons = ['б', 'в', 'г', 'д', 'ж', 'з', 'й', 'к', 'л', 'м', 'н', 'п', 'р', 'с', 'т', 'ф', 'х', 'ц', 'ч', 'ш', 'щ']
russian_cons_str = ''.join(russian_cons)

extra_whitespace = re.compile('\s+', re.U)
repeated_chars = re.compile('([а-яa-z])\1\1+', re.U)
tsa_ending = re.compile('(.+)(цца|ццо)$', re.U)
vobsch_reg = re.compile('в(о|а){1,2}(б|п)щ{1,2}(е|и)м', re.U)
potomy_reg = re.compile('п(о|а)т(о|а)му\s?(ч|ш)т(о|а)', re.U)

frequent_intentional_mistakes = {'собстно': 'собственно', 'собсна': 'собственно', "многабуков": "много букв",
                                 "седня": "сегодня", "естесно": "естественно", "ессно": "естественно",
                                 "естессно": "естественно", "ничо": "ничего", "неоч": "не очень", "щаз": "сейчас",
                                 "какбы": "как бы", "какбе": "как бы", "скока": "сколько", "нащщот": "насчет",
                                 "ваще": "вообще", "ващще": "вообще"}

frequent_hyphen_space_mistakes = {"изза": "из-за", "еслиб": "если б", "тоесть": "то есть", "всмысле": "в смысле",
                                  "такчто": "так что"}

hyphen_endings = ['либо', 'нибудь', "то"]
subj_particles = ["кто", "как", "если", "когда", "вот", "хоть", "пусть"]
hyphen_beg = ["вице", "камер", "контр", "лейб", "обер", "статс", "унтер", "флигель", "штаб", "штабс", "экс"]


def tokenize(text, punct_include=False):
    tokens = nltk.word_tokenize(text)
    if punct_include:
        return tokens

    return [i for i in tokens if i not in string.punctuation]


def clean_text(text):
    # at first, replace most popular mistakes
    text = vobsch_reg.sub(" в общем ", text)
    text = potomy_reg.sub(" потому что ", text)

    text = extra_whitespace.sub(' ', text)
    text = text.lower()
    text = text.replace('_', ' ')
    text = text.replace('...', '.')
    text = text.replace('ё', 'е')

    return text


def neighborhood(iterable):
    """
    Iterator wrapper, which gives access to prev and next elements
    """
    iterator = iter(iterable)
    prev = None
    curr = next(iterator)

    for nxt in iterator:
        yield (prev, curr, nxt)
        prev = curr
        curr = nxt

    yield (prev, curr, None)


def correct_hyphens_spaces(words):
    corrected = []
    skip_next = False

    for prev, word, nxt in neighborhood(words):
        if skip_next:
            skip_next = False
            continue
        n_corrected = len(corrected)

        # проверяем "не" с глаголом
        if word.startswith('не'):
            if ma.parse(word[2:])[0].tag.POS == 'VERB':
                corrected.append('не')
                corrected.append(word[2:])
                continue

        if word in frequent_hyphen_space_mistakes:
            word = frequent_hyphen_space_mistakes[word]
            if ' ' in word:
                # если одно слово заменили на несколько
                for sub_word in word.split(' '):
                    corrected.append(sub_word)
                continue

        if word.endswith("бы"):
            if word[:-2] in subj_particles:
                corrected.append(word[:-2])
                corrected.append("бы")
                continue

        # дефисы
        if '-' not in word:
            # кое-, кой-
            if word.startswith('кое') or word.startswith("кой"):
                # если приставку написали как отдельное слово - соединяем со следующим
                if len(word) == 3:
                    if len(nxt) > 1:
                        corrected.append(word + "-" + nxt)
                        skip_next = True
                        continue
                else:
                    # если часть слова после приставки есть в нашем словаре - вставляем дефис
                    if word[3:] in pt:
                        corrected.append(word[:3] + "-" + word[3:])
                        continue

            # вице-, камер-, контр-, лейб-, обер-, статс-, унтер-, флигель-, штабс- и экс-
            for beg in hyphen_beg:
                if word.startswith(beg):
                    corrected.append("{0}-{1}".format(beg, word[len(beg):]))
                    continue
            # пол-
            if word.startswith('пол'):
                if word[3:].startswith('л'):
                    corrected.append("пол-{0}".format(word[3:]))
                    continue

            # -либо, -нибудь, -то
            for ending in hyphen_endings:
                if word.endswith(ending):
                    # вставляем дефис если часть слова без окончания есть в словаре
                    first_part = word[:-len(ending)]
                    if first_part in pt:
                        corrected.append("{0}-{1}".format(first_part, ending))

        # если за эту итерацию мы еще не добавляли слов - добавляем исходное
        if n_corrected == len(corrected):
            corrected.append(word)

    return corrected


def correct_intentional_misspelling(words):
    corrected = []
    for word in words:
        if word not in pt:
            # все повторяющиеся символы (от 3 и более) заменяются на один
            word = repeated_chars.sub('\\1', word)

            if word in frequent_intentional_mistakes:
                word = frequent_intentional_mistakes[word]
                if ' ' in word:
                    # если одно слово заменили на несколько
                    for sub_word in word.split(' '):
                        corrected.append(sub_word)
                    continue
                # заменяем окончания типа -цца и -ццо
                word = tsa_ending.sub('\\1ться', word)

        corrected.append(word)

    return corrected


def preprocess_text(text, punct_include=False):
    text = clean_text(text)

    words = tokenize(text, punct_include)
    words = numbers2letters(words)
    words = correct_intentional_misspelling(words)
    words = correct_hyphens_spaces(words)

    return words


if __name__ == '__main__':
    ma = pymorphy2.MorphAnalyzer()
    pt = {"чего", "что", "кто", "в", "наконец", "не", "как", "пицца", "когда", "кем"}

    with open('test_file.txt', encoding='utf-8') as f:
        test_text = f.read()

    res = preprocess_text(test_text)
    for r in res:
        print(r)

