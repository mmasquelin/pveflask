import json
import re


def is_word_in_text(word, text):
    """
    Check if a word is in a text.

    Parameters
    ----------
    word : str
    text : str

    Returns
    -------
    bool : True if word is in text, otherwise False.

    Examples
    --------
    >>> is_word_in_text("Python", "python is awesome.")
    True

    >>> is_word_in_text("Python", "camelCase is pythonic.")
    False

    >>> is_word_in_text("Python", "At the end is Python")
    True
    """
    pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
    pattern = re.compile(pattern, re.IGNORECASE)
    word = re.escape(word)
    matches = re.search(pattern, text)
    return bool(matches)


def pp_json(json_string):
    # converts json to dict then back to string... ridiculous but not pointless
    print(json.dumps(json.loads(json_string), sort_keys=True, indent=4))
    return
