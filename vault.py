import pandas as pd
from collections import Counter, defaultdict
from classes.product_class import Product
from classes.clothing_class import Clothing
from utils.headers import *



def check_duplicates(products: list, all_products: list) -> dict[int, int]:
    """ Returns dictionary of what item codes are already used in the full list.
    """
    duplicates = {}
    for product in products:
        if product.plu_code in all_products:
            duplicates[product.plu_code] = all_products.index(product.plu_code)
    return duplicates



def get_all_plu(path: str) -> list[int]:
    """ Read an excel of all AVOCA products into a list of PLU codes """
    plu_df = pd.read_excel(path)
    plu_df.columns = plu_df.columns.str.lower().str.strip().str.replace(" ", "").str.replace("_", "").str.replace("-", "")
    if "plu" not in plu_df.columns:
        raise KeyError("Missing 'plu' column after normalization.")

    return plu_df["plu"].tolist()



def find_internal_duplicates(products: list[Product]) -> list[str]:
    """Checks for duplicate PLU codes within the new product file."""
    counts = Counter(product.plu_code for product in products)
    errors = []
    for plu, count in counts.items():
        if count > 1:
            lines = [product.excel_line for product in products if product.plu_code == plu]
            errors.append(f"PLU Code: {plu} appears {count} times on lines {lines}")
    return errors



def load_products(path: str) -> list[Product]:
    """Load the new product file into a list of Clothing class objects"""
    df = pd.read_excel(path)
    messages = []

    def get_col(key):
        col, msg, msg_type = find_header(df, PRODUCT_HEADER_MAP[key])
        if msg:
            messages.append((msg, msg_type))
        return col


    products = []
    for idx, row in df.iterrows():
        line_number = idx + 2
        product = Product(
            code = row.get(get_col("plu_code")),
            description = row.get(get_col("description")),
            subgroup = row.get(get_col("subgroup")),
            supplier_code = row.get(get_col("supplier_code")),
            season = row.get(get_col("season")),
            main_supplier = row.get(get_col("main_supplier")),
            cost_price = row.get(get_col("cost_price")),
            barcode = row.get(get_col("barcode")),
            vat_rate = row.get(get_col("vat_rate")),
            rrp = row.get(get_col("rrp")),
            sell_price = row.get(get_col("sell_price")),
            stg_price = row.get(get_col("stg_price")),
            tarriff = row.get(get_col("tarriff")),
            web = row.get(get_col("web")),
            idx = line_number
        )
        products.append(product)

 
    return products, messages



def load_clothing(path: str) -> list[Clothing]:

    """Load the new clothing file into a list of Clothing class objects"""
    df = pd.read_excel(path)
    clothes = []
    get_col = lambda key: find_header(df, CLOTHING_HEADER_MAP[key])
    for idx, row in df.iterrows():
        line_number = idx + 2
        clothing = Clothing(
            code = row.get(get_col("style_code")),
            description = row.get(get_col("description")),
            size = row.get(get_col("size")),
            colour = row.get(get_col("colour")),
            subgroup = row.get(get_col("subgroup")),
            supplier_code = row.get(get_col("supplier_code")),
            season = row.get(get_col("season")),
            main_supplier = row.get(get_col("main_supplier")),
            cost_price = row.get(get_col("cost_price")),  # Note: products use "cost_price"
            barcode = row.get(get_col("barcode")),
            vat_rate = row.get(get_col("vat_rate")),
            rrp = row.get(get_col("rrp")),
            sell_price = row.get(get_col("sell_price")),
            stg_price = row.get(get_col("stg_price")),  # products: "stg_price", clothing: "stgretailprice"
            tarriff = row.get(get_col("tarriff")),
            brand = row.get(get_col("brand")),
            product_type = row.get(get_col("product_type")),
            web = row.get(get_col("web")),
            country = row.get(get_col("country")),
            country_code = row.get(get_col("country_code")),
            idx = line_number
        )
        clothes.append(clothing)
    return clothes


def read_column(df: pd.DataFrame, possible_names) -> list:
    """Find the given column name and return that column as a list.
    Converts all objects to strings"""
    # if isinstance(possible_names, str):
    #     possible_names = [possible_names]
    # # try:
    #     # df = pd.read_excel(file_path)
    #     # normalized_cols = {normalize_header(col): col for col in df.columns}

    # # Exact match with key map
    #     for name in possible_names:
    #         normalized = normalize_header(name)
    #         if normalized in normalized_cols:
    #             return df[normalized_cols[normalized]].dropna().apply(normalizer).tolist(), "", "skip"

    # # Char match
    #     best_score = 0
    #     best_possible = None
    #     original_header = None
        
    #     for df_col_key, df_col_val in normalized_cols.items():
    #             for expected_name in possible_names:
    #                 score = char_match(expected_name, df_col_key)
    #                 if score > best_score:
    #                     best_score = score
    #                     best_possible = expected_name
    #                     original_header = df_col_val
        
    #     if best_score >= THRESHOLD:  # ← adjust threshold as needed
    #         msg = f"CHAR_MATCH updated the column header '{original_header}' to '{best_possible}' to match template spreadsheet"
    #         return df[best_possible].dropna().apply(normalizer).tolist(), msg, "alert"
    #     return [], possible_names[0], "error"

    # except Exception as e:
    #     return [], f"Error reading {file_path}: {e}", "error"




