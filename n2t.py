# -*- coding: utf-8 -*-

import pymorphy2
morph = pymorphy2.MorphAnalyzer()
import re
import pytils


def case_for_many_words(words, case):
    new_string = ''
    words = words.split()
    for word in words:
        word_parsed = morph.parse(word)[0]
        new_string += word_parsed.inflect({case})[0] + ' '
    return new_string


def case_for_one_word(word, case):
    text_parsed = morph.parse(word)[0]
    new_string = text_parsed.inflect({case})[0]
    return new_string


def transform(number, case):
    number = int(number.group(1))
    text = pytils.numeral.in_words(number)
    if ' ' not in text:
        result = case_for_one_word(text, case)
    else:
        result = case_for_many_words(text, case)
    return result


def change(word):
    gen = re.compile('(\d*?)-?\w*?((о?го)|((у|е|ё)?х)|и|а)$')
    dat = re.compile('(\d*?)-?\w*?((о?му)|((у|е|ё)?м)|и|а)$')
    abl = re.compile('(\d*?)-?\w*?(((у|е)?мя)|[тм]?ь?ю)$')
    loc = re.compile('(\d*?)-?\w*?(((у|е|ё)?х)|([тм]?и))$')
    m = gen.search(word)
    if m is not None:
        result = transform(m, 'gent')
    else:
        m = dat.search(word)
        if m is not None:
            result = transform(m, 'datv')
        else:
            m = abl.search(word)
            if m is not None:
                result = transform(m, 'ablt')
            else:
                m = loc.search(word)
                if m is not None:
                    result = transform(m, 'loct')
                else:
                    result = word
    print(result)


def numbers2letters(words):
    return [change(w) for w in words]

