import pandas as pd

from classes.product_class import Product
from classes.clothing_class import Clothing
from utils.headers import *
from utils.validators import *



def load_products(df: pd.DataFrame) -> tuple[list[Product], list[tuple[str, str]]]:
    """Load the new product file into a list of Product class objects"""
    # expected_headers = [name for sublist in PRODUCT_HEADER_MAP.values() for name in sublist]

    messages = []
    
    # Pre-resolve all needed column names
    used_columns = set()
    col_map = {}
    for key in PRODUCT_HEADER_MAP:
        col, message, type = find_header(df, PRODUCT_HEADER_MAP[key], used_columns)
        if col:
            used_columns.add(col)
        col_map[key] = col  # May be None if not found
        if message:
            messages.append((message, type))

    # Build Product objects using resolved column names
    products = []
    for idx, row in df.iterrows():
        line_number = idx + 2
        product = Product(
            code = row.get(col_map["plu_code"]),
            description = row.get(col_map["description"]),
            subgroup = row.get(col_map["subgroup"]),
            supplier_code = row.get(col_map["supplier_code"]),
            season = row.get(col_map["season"]),
            main_supplier = row.get(col_map["main_supplier"]),
            cost_price = row.get(col_map["cost_price"]),
            barcode = row.get(col_map["barcode"]),
            vat_rate = row.get(col_map["vat_rate"]),
            rrp = row.get(col_map["rrp"]),
            sell_price = row.get(col_map["sell_price"]),
            stg_price = row.get(col_map["stg_price"]),
            tarriff = row.get(col_map["tarriff"]),
            web = row.get(col_map["web"]),
            idx = line_number
        )
        products.append(product)

    return products, messages


def load_clothing(df: pd.DataFrame) -> tuple[list[Clothing], list[tuple[str, str]]]:
    """Load the new clothing file into a list of Clothing class objects"""
    # expected_headers = [name for sublist in CLOTHING_HEADER_MAP.values() for name in sublist]
    # header_row = detect_header_row(df, expected_headers)  # <- use your existing detection function
    # df = pd.read_excel(path, header=header_row)
    # df.columns = df.columns.str.lower().str.strip().str.replace(" ", "")
    # df.columns = [normalize_header(col) for col in df.columns]

    messages = []
    col_map = {}

    # Step 1: Resolve headers
    for key, possible_names in CLOTHING_HEADER_MAP.items():
        col, message, type = find_header(df, possible_names)
        if message:
            messages.append((message, type))
        col_map[key] = col

    # Step 2: Check for required columns
    for key, col in col_map.items():
        if col is None and key in ["style_code", "description"]:  # Add more keys if needed
            raise ValueError(f"Missing required column: {key}")

    # Step 3: Build clothing objects
    clothes = []
    for idx, row in df.iterrows():
        line_number = idx + 2
        clothing = Clothing(
            code=row.get(col_map["style_code"]),
            description=row.get(col_map["description"]),
            size=row.get(col_map["size"]),
            colour=row.get(col_map["colour"]),
            subgroup=row.get(col_map["subgroup"]),
            supplier_code=row.get(col_map["supplier_code"]),
            season=row.get(col_map["season"]),
            main_supplier=row.get(col_map["main_supplier"]),
            cost_price=row.get(col_map["cost_price"]),
            barcode=row.get(col_map["barcode"]),
            vat_rate=row.get(col_map["vat_rate"]),
            rrp=row.get(col_map["rrp"]),
            sell_price=row.get(col_map["sell_price"]),
            stg_price=row.get(col_map["stg_price"]),
            tarriff=row.get(col_map["tarriff"]),
            brand=row.get(col_map["brand"]),
            product_type=row.get(col_map["product_type"]),
            web=row.get(col_map["web"]),
            country=row.get(col_map["country"]),
            country_code=row.get(col_map["country_code"]),
            idx=line_number
        )
        clothes.append(clothing)

    return clothes, messages



def read_column(df: pd.DataFrame, possible_names, used_columns=None) -> list:
    """Find the given column name and return that column as a list.
    Converts all objects to strings"""
    if isinstance(possible_names, str):
        possible_names = [possible_names]

    if used_columns is None:
        used_columns = set()

    col_name, msg, msg_type = find_header(df, possible_names, used_columns)
    if col_name is not None and col_name in df.columns:
        used_columns.add(col_name)
        return df[col_name].dropna().apply(normalizer).tolist(), msg, msg_type
    return [], msg, msg_type



# df = pd.read_excel(YOUNGS_UPLOAD)
# df.columns = [col.strip().lower().replace(" ", "") for col in df.columns]  # Optional: normalize columns

# products, messages = load_products(df)

# print(products[:5])

