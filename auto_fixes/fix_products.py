import pandas as pd
from decimal import Decimal
import math

from utils.contants import *
from utils.headers import *


def fix_description(df: pd.DataFrame):
    """ Remove any bad characters and shorten the description to just 50 characters"""
    changes = []
    desc_col, *_ = find_header(df, PRODUCT_HEADER_MAP["description"], used_columns=None)
    if desc_col is None or desc_col not in df.columns:
        return df, []

    for i, desc in df[desc_col].items():
        if isinstance(desc, str):
            og_desc = desc
            final = desc

            if len(desc) > 50:
                final = desc[:50]
                changes.append(f"Line {i+2} \u00A0\u00A0|\u00A0\u00A0 Long description: '{og_desc}' shortened to '{final}'")
            if desc != final:
                df.at[i, desc_col] = final
    return df, changes



def fix_decimals(df: pd.DataFrame):
    """ Numbers have to be rounded to 2 decimal places"""
    columns = ["cost_price", "rrp", "selling_price", "stg_price"]
    changes = []

    for key in columns:
        col_name, *_ = find_header(df, PRODUCT_HEADER_MAP[key], used_columns=None)
        if col_name is None or col_name not in df.columns:
            continue

        for i, num in df[col_name].items():
            if isinstance(num, (int, float)) and not math.isnan(num):
                decimal_val = Decimal(str(num))
                if -decimal_val.as_tuple().exponent > 2:
                    new_num = round(num, 2)
                    df.at[i, col_name] = new_num
                    changes.append(f"Line {i+2} \u00A0\u00A0|\u00A0\u00A0 {col_name} of {num} rounded to {new_num}")
    return df, changes



def fix_vat(df: pd.DataFrame):
    """Assign the correct VAT codes for given percentages"""
    changes = []

    vat_col, *_ = find_header(df, PRODUCT_HEADER_MAP["vat_rate"], used_columns=None) 
    if vat_col is None or vat_col not in df.columns:
        return df, []

    for i, vat in df[vat_col].items():
        if vat in VAT_CODES:
            new_vat = VAT_CODES[vat]
            df.at[i, vat_col] = new_vat
            changes.append(f"Line {i+2} \u00A0\u00A0|\u00A0\u00A0 VAT Rate {vat} updated to code {new_vat}")
    return df, changes



def fix_bad_char(df: pd.DataFrame) -> str:
    """ The characters ',% can't be in any product variables. Check if they have any and return where.
        Input for id_attr should be the code/name of item preferred when returning an error message.
    """
    changes = []
    for col in df.columns:
        if df[col].dtype == object:
            for i, val in df[col].items():
                if isinstance(val, str):          # Avoid type error
                    cleaned = ''.join(char for char in val if char not in BAD_CHARS)

                    if val != cleaned:
                        df.at[i, col] = cleaned
                        changes.append(f"Line {i} \u00A0\u00A0|\u00A0\u00A0 Bad characters removed from column '{col}'")

    return df, changes



def update_all_products(df: pd.DataFrame):
    df = df.copy()   
    changes_by_type = {}

    df, desc_changes = fix_description(df)
    changes_by_type["Description Fixes"] = desc_changes

    df, char_changes = fix_bad_char(df)
    changes_by_type["Bad Char Fixes"] = char_changes

    # df, decimal_changes = fix_decimals(df)
    # changes_by_type["Decimal Fixes"] = decimal_changes

    df, vat_changes = fix_vat(df)
    changes_by_type["VAT Fixes"] = vat_changes

    return df, changes_by_type





