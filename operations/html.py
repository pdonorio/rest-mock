# -*- coding: utf-8 -*-

import lxml.html
import lxml.etree


def convert(html_text):
    try:
        document = lxml.html.document_fromstring(html_text)
    except (lxml.etree.ParserError, lxml.etree.XMLSyntaxError, ValueError) as e:
        # empty document
        return ''

    raw_text = document.text_content()
    return raw_text

