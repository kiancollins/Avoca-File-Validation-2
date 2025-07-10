import pandas as pd

from classes.product_class import Product
from classes.clothing_class import Clothing
from utils.headers import *
from utils.normalizer import normalizer, normalize_header
from utils.contants import *


def check_exist(items: list[Product | Clothing], full_list: list, attr: str) -> tuple[dict, dict]:
    """ Returns dictionary of what item codes are already used in the full list. """
    nonexist = []

    # Normalize full list once
    full_list_cleaned = [normalizer(str(x)) for x in full_list]

    for idx, item in enumerate(items):
        code = normalizer(str(getattr(item, attr, "")))  # Make sure it's a str before normalizing
        if code not in full_list_cleaned:
            nonexist.append(f"Line {idx+2} \u00A0\u00A0|\u00A0\u00A0 {item} does not currently exist in data base. Cannot amend price.")

    return nonexist


