"""
Validators

Common validation checks done on uploaded files
"""
from classes.product_class import *
from classes.clothing_class import *
from utils.normalizer import *
from utils.contants import *
from collections import defaultdict, Counter



def check_duplicates(items: list[Product | Clothing], full_list: list, attr: str) -> dict[int, int]:
    """ Returns dictionary of what item codes are already used in the full list.
        attr should be entered as the class variable name 
    """
    duplicates = {}
    for item in items:
        value = normalizer((getattr(item, attr, None)))
        if value in full_list:
            duplicates[value] = full_list.index(value)
    return duplicates


def duplicate_barcodes(items: list[Product | Clothing], attr:str) -> list[str]:
    """ Checks to see if any products in new product file has the same barcodes."""
    barcode_to_code = defaultdict(list)
    error_list = []

    for item in items:
        if item.barcode:  # Skip empty or None
            id = normalizer(getattr(item, attr, None))
            barcode_to_code[item.barcode].append((id, item.excel_line))

    for barcode, codes in barcode_to_code.items():
        if len(codes) > 1:
            detail = ", ".join([f"{code} (line {line})" for code, line in codes])
            error_list.append(f"Barcode {barcode} is shared by: {detail}")
            # print(f"Barcode {barcode} is shared by Products: {plu_list}")
            # st.write(f"Barcode {barcode} is shared by Products: {plu_list}")

    if len(error_list) > 0:
        return error_list
    return None


def check_internal_duplicates(items: list[Product | Clothing], attr:str) -> dict[int, int]:
    """ Checks if there are any duplicate codes within the new file
        attr should be entered as the class variable name """
    errors = []
    values = [normalizer(getattr(item, attr, None)) for item in items]
    counts = Counter(values)
    for code, count in counts.items():
        if count > 1:
            lines = [item.excel_line for item in items if normalizer(getattr(item, attr, None)) == code]
            errors.append(f"Code: {code} appears {count} times on lines {lines}")
    return errors


def check_clothing_duplicates(items: list[Clothing]):
    """ Check if there are duplicate clothing items within a new file. 
        Clothing is done differently since there can be multiple style codes with different sizes.
    """
    exists = set()
    errors = []

    for item in items:
        key = (item.style_code, item.size, item.colour)
        if key in exists:
            errors.append(f"Duplicate Style {item.style_code} with size {item.size} on line {item.excel_line}")
        else:
            exists.add(key)
    return errors


def bad_char(obj, id_attr: str) -> str:
    """ The characters ',% can't be in any product variables. Check if they have any and return where.
        Input for id_attr should be the code/name of item preferred when returning an error message.
    """
    bad_fields = []
    for field, value in vars(obj).items():     # Grab each variable and the value for the product
            if isinstance(value, str):          # Avoid type error
                if any(char in value for char in BAD_CHARS):    # Check if any bad chars are in the value
                    bad_fields.append(field)

    if bad_fields:
            line = getattr(obj, "excel_line", None)
            id = getattr(obj, id_attr, None)
            return f"Line {line} \u00A0\u00A0|\u00A0\u00A0 {id} contains invalid character(s) {BAD_CHARS}"



