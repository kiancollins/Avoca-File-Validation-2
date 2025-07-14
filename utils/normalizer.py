"""
Normalizer

Functions used for normalizing everything for the program. Mostly for fixing headers.
"""


def normalizer(value):
    """ Given value is outputted as a string."""
    value = str(value).strip()
    # if value.endswith(".0"):
    #     value = value[:-2]
    return value

def normalize_header(value):
    """ Given header is outputted in a normalized format"""
    return str(value).strip().lower().replace(" ", "").replace("_", "").replace("-", "")


def char_match(target: str, possible: str):
    """ Returns a score of how close two words are based on matching characters
    
    >>> char_match("costprice", "costp ricee")
    0.9

    >>> char_match("description", "descripshun")  # 2 wrong letters
    0.6363636363636364

    >>> char_match("vatcode", "vat-code")  # assuming normalize_header removes dashes
    1.0

    >>> char_match("productname", "product_id")
    0.5384615384615384

    >>> char_match("name", "nmae")  # wrong order, but same letters
    1.0

    >>> char_match("three digit supplier", "3 digit supplier")
    0.84375
    """
    target = normalize_header(target)
    possible = normalize_header(possible)
    target_list = list(target)
    possible_list = list(possible)
    unmatched_list = []

    for char in possible_list:
        if char in target_list:
            target_list.remove(char)
        else:
            unmatched_list.append(char)
        
    total_possible = len(target) + len(possible)
    total = len(unmatched_list) + len(target_list)
    score = 1 - (total / total_possible)
    return score




