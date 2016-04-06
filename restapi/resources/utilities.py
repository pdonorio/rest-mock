# -*- coding: utf-8 -*-

""" Common utilities """


def split_and_html_strip(string):
    """ Compute words from transcriptions """
    words = []
    START = '<'
    END = '>'
    skip = False
    word = ""
    for char in string:
        if char == START:
            skip = True
            continue
        elif char == END:
            skip = False
            continue
        if skip:
            continue
        if char.isalpha():
            word += char
        elif word != "" and len(word) > 3:
            words.append(word)  # word.lower())
            word = ""

    if not skip:
        words.append(word)

    return set(words)
