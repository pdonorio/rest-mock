# -*- coding: utf-8 -*-

""" Common utilities """

WORD_MIN_LENGTH = 4


def split_and_html_strip(string):
    """ Compute words from transcriptions """
    words = []
    START = '<'
    END = '>'
    skip = False
    word = ""
    for char in string:

        # HTML tags/attributes: skip
        if char == START:
            skip = True
            continue
        elif char == END:
            skip = False
            continue
        if skip:
            continue

        # Real words (without symbols and numbers)
        if char.isalpha():
            word += char
        elif word != "" and len(word) >= WORD_MIN_LENGTH:
            words.append(word)  # word.lower())
            word = ""

    # Do not skip last word
    if not skip and len(word) >= WORD_MIN_LENGTH:
        words.append(word)

    return set(words)
