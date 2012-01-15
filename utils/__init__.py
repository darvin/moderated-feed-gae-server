import lxml.html

def strip_string(st):
    return filter(lambda c: c.isalnum() and ord(c) < 128, lxml.html.document_fromstring(st).text_content())