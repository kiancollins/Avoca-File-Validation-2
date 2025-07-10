"""
Headers

Functions for working with headers.
"""
import pandas as pd
from utils.contants import *
from utils.normalizer import *


def detect_header_row(file_path, expected_headers, max_rows=10):
    preview_df = pd.read_excel(file_path, header=None, nrows=max_rows)

    best_row = 0
    best_score = 0

    # print("===== SCANNING HEADER CANDIDATES =====")
    for i in range(min(max_rows, len(preview_df))):
        row = preview_df.iloc[i].fillna("").astype(str).tolist()
        normalized_row = [normalize_header(cell) for cell in row]

        # print(f"\nRow {i}: {row}")
        # print(f"Normalized: {normalized_row}")

        matches = 0
        for header in expected_headers:
            norm_header = normalize_header(header)
            best_header_score = max(char_match(norm_header, col) for col in normalized_row)
            if best_header_score >= THRESHOLD:
                matches += 1
            # print(f"→ Checking header '{header}' (normalized: '{norm_header}') → best score: {best_header_score:.2f}")

        match_ratio = matches / len(expected_headers)
        # print(f"Match ratio for row {i}: {match_ratio:.2f}")

        if match_ratio > best_score:
            best_score = match_ratio
            best_row = i
            # print(f" \n ------------ \n {best_row}, {best_score}")

    # print(f"===== BEST ROW: {best_row} (score: {best_score:.2f}) =====")
    return (best_row) if best_score >= 0.3 else 0



def find_header(df: pd.DataFrame, possible_names: dict, used_columns: set[str]):
    """ Identify column based on a possible names reference dictionary.
        If reference dictionary doesn't work, use char match. """
    normalized_cols = {normalize_header(col): col for col in df.columns}
    possible_normalized = [normalize_header(name) for name in possible_names]

    if used_columns is None:
        used_columns = set()


        # Main: Exact match
    for name in possible_normalized:
        if name in normalized_cols:
            col_name = normalized_cols[name]
            if col_name not in used_columns:
                return col_name, "", "skip"

    # Back up: Char match
    best_score = 0
    best_possible = None
    original_header = None

    for col_key in normalized_cols.keys():
        if normalized_cols[col_key] in used_columns:
            continue
        for name in possible_names:
            score = char_match(normalize_header(name), col_key)
            if score > best_score:
                best_score = score
                best_possible = name
                original_header = normalized_cols[col_key]
    
    if best_score >= THRESHOLD:  # ← adjust threshold as needed
        msg = f"CHAR_MATCH updated the column header '{original_header}' to '{best_possible}' to match template spreadsheet"
        return original_header, msg, "alert"
    
    print(f"No match found for key — returning None: {possible_names}")
    return None, possible_names[0], "error"


def check_missing_headers(df: pd.DataFrame, header_map: dict[str, list[str]]) -> list[str]:
    """
    Checks for missing expected headers in a DataFrame using a HEADER_MAP.
    
    Returns a list of standardized keys (like 'plu_code', 'style_code') 
    for which none of the possible column names were found.
    """
    normalized_df_cols = {normalize_header(c) for c in df.columns}
    missing = []

    for key, possibilities in header_map.items():
        found = any(normalize_header(name) in normalized_df_cols for name in possibilities)
        if not found:
            missing.append(key)
    return missing

