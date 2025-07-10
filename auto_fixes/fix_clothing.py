import pandas as pd
from decimal import Decimal
import math

from utils.contants import *
from utils.headers import *



def fix_description(df: pd.DataFrame):
    """ Shorten the description to just 50 characters"""
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
    """Update the decimal rounding/format to the correct 2 decimal places"""
    columns = ['costprice', 'rrp', 'sellingprice', 'stgprice']
    changes = []
    for column in columns:
        if column not in df.columns:
            continue
        for i, num in df[column].items():
            if isinstance(num, (int, float)) and not math.isnan(num):
                decimal_val = Decimal(str(num))
                if -decimal_val.as_tuple().exponent > 2:
                    new_num = round(num, 2)
                    df.at[i, column] = new_num
                    changes.append(f"Line {i+2} \u00A0\u00A0|\u00A0\u00A0 {column} of {num} rounded to {new_num}")
    return df, changes




def fix_vat(df: pd.DataFrame):
    """Assign the correct VAT codes for given percentages"""
    changes = []
    for i, vat in df['vatrate'].items():
        if vat in VAT_CODES:
            new_vat = VAT_CODES[vat]
            df.at[i, 'vatrate'] = new_vat
            changes.append(f"Line {i+2} \u00A0\u00A0|\u00A0\u00A0 VAT Rate {vat} updated to code {new_vat}")
    return df, changes



def fix_color(df: pd.DataFrame):
    """Shorten colour descriptions that are over 10 characters. Also remove bad characters"""
    changes = []
    # color_col, *_ = find_column(df, PRODUCT_HEADER_MAP["colour"])

    if "colour" not in df.columns:
        return df, []

    for i, desc in df["colour"].items():
        if isinstance(desc, str):
            og_desc = desc
            cleaned = ''.join(c for c in desc if c not in BAD_CHARS)
            final = cleaned

            if og_desc != cleaned:
                changes.append(f"Line {i+2} \u00A0\u00A0|\u00A0\u00A0 Bad characters removed from color description: '{og_desc}', updated to '{cleaned}'")
            if len(cleaned) > 10:
                final = cleaned[:10]
                changes.append(f"Line {i+2} \u00A0\u00A0|\u00A0\u00A0 Long color description: '{og_desc}' shortened to '{final}'")
            if desc != final:
                df.at[i, "colour"] = final
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





def update_all_clothing(df: pd.DataFrame):
    df = df.copy()
    
    changes = {}

    df, desc_changes = fix_description(df)
    changes["Description Fixes"] = desc_changes

    df, char_changes = fix_bad_char(df)
    changes["Bad Char Fixes"] = char_changes

    df, decimal_changes = fix_decimals(df)
    changes["Decimal Fixes"] = decimal_changes

    df, vat_changes = fix_vat(df)
    changes["VAT Fixes"] = vat_changes

    df, color_changes = fix_color(df)
    changes["Color Fixes"] = color_changes

    return df, changes



