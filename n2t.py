# coding: utf-8
import pymorphy2
import re
import pytils
import string

from collections import OrderedDict

RE_CASE = OrderedDict()
RE_CASE['gent'] = re.compile('^(\d+)-?\w*((о?го)|((у|е|ё)?х)|и|а)$')
RE_CASE['datv'] = re.compile('^(\d+)-?\w*((о?му)|((у|е|ё)?м)|и|а)$')
RE_CASE['ablt'] = re.compile('^(\d+)-?\w*(((у|е)?мя)|[тм]?ь?ю)$')
RE_CASE['loct'] = re.compile('^(\d+)-?\w*(((у|е|ё)?х)|([тм]?и))$')

ma = pymorphy2.MorphAnalyzer()


def case_for_numerical(text, case):
    return ' '.join([ma.parse(w)[0].inflect({case})[0] for w in text.split()])


def replace(text):
    for case, regex in RE_CASE.items():
        match = regex.search(text)
        if match:
            numerical = pytils.numeral.in_words(int(match.group(1)))
            return case_for_numerical(numerical, case)

    return text


def numbers2letters(words):
    return [replace(w) if w[0] in string.digits else w for w in words]


print(numbers2letters(['29ти']))
