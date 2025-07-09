"""
Constants

Constant variables that get called throughout this program
"""


NEW_PRODUCTS_GARDEN = "Spreadsheets/0107025 GARDEN FRESH.xlsx" 
NEW_PRODUCTS_JAVADO = "Spreadsheets/JAVADO UPLOAD.xlsx"
PLU_ACTIVE = "Spreadsheets/PLU-Active-List.xlsx"
CLOTHING_UPLOAD = "Spreadsheets/lothing upload example.xlsx"
FULL_CLOTHING = "Spreadsheets/full_clothing_listing.xlsx"
BAD_PROD_UPLOAD = "Spreadsheets/NG New Product 080425.xlsx"


ERROR_TYPES = {
    # Product checks
    "Duplicate PLU Code Errors": "PLU Codes are all valid.", 
    "Duplicate PLUs Within Uploaded File": "No Duplicate PLU Codes.",
    "PLU Code Length Errors": "PLU Code lengths are all valid.",
    "Product Description Length Errors": "Product descriptions are all valid.",
    "Decimal Formatting Errors": "All numbers rounded correctly.",

    # Shared
    "Unusable Character Errors": "No unusable characters found.",
    "Duplicate Barcode Errors": "All barcodes are valid.",

    # Clothing checks
    "Duplicate Style Code Code Errors": "Style Codes are all valid.",
    "Duplicate Style Codes Within Uploaded File": "No Duplicate Style Codes.",
    "Style Code Length Errors": "Style Code lengths are all valid.",
    "Clothing Item Description Length Errors": "Descriptions are all valid.",
}


VAT_CODES = {0.0: 0,
             23.0: 1,
             13.5: 2,
             9.0: 3}


BAD_CHARS = set("',%")


THRESHOLD = 0.8 


PRODUCT_HEADER_MAP = {
    "plu_code": ["plu", "plu code", "plucode", "plu-code", "plu_code"],
    "description": ["description", "desc"],
    "subgroup": ["subgroup", "category", "sub", "subcategory"],
    "supplier_code": ["3digitsupplier", "suppliercode", "threedigitsupplier", "3digitsuppliercode", "threedigitsuppliercode"],
    "season": ["season"],
    "main_supplier": ["mainsupplier", "main-supplier", "supplier", ],
    "cost_price": ["costprice", "cost"],
    "barcode": ["barcode", "bar code"],
    "vat_rate": ["vatrate", "vat", "vatcode", "vat-code"],
    "rrp": ["rrp"],
    "sell_price": ["sellingprice", "sellprice", "priceforsell", "selling"],
    "stg_price": ["stgprice", "stgretailprice", "sterlingprice"],
    "tarriff": ["tarriffcode", "tarrif"],
    "web": ["web"]
    
}


CLOTHING_HEADER_MAP = {
    "style_code": ["stylecode", "style code", "style-code", "style_code"],
    "description": ["description", "desc"],
    "size": ["size"],
    "colour": ["colour", "color"],
    "subgroup": ["subgroup", "category", "sub group"],
    "supplier_code": ["3digitsupplier", "supplier code", "suppliercode"],
    "season": ["season"],
    "main_supplier": ["mainsupplier", "main supplier"],
    "cost_price": ["costprice", "cost price", "cost"],
    "barcode": ["barcode", "bar code"],
    "vat_rate": ["vatrate", "vat rate", "vat", "vatcode"],
    "rrp": ["rrp"],
    "sell_price": ["sellingprice", "selling price", "sellprice"],
    "stg_price": ["stgretailprice", "stg retail price", "stgprice"],
    "tarriff": ["tarriffcode", "tarriff code", "tariff", "tarrif"],
    "brand": ["brandinstore", "brand in store", "brand"],
    "product_type": ["producttype", "product type"],
    "web": ["web", "online", "website"],
    "country": ["countryoforigin", "country of origin", "origin"],
    "country_code": ["countrycode", "country code"],
}



