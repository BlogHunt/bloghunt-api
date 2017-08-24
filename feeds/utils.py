""" A collection of various utility functions used to import/parse feeds.

author: Brian Schrader
"""

import requests


def encoded_text_from_url(url, should_raise=True):
    response = requests.get(url)
    if should_raise:
        response.raise_for_status()
    return response.text.encode()
