import pandas as pd
import streamlit as st
import io

from converter import * 
from auto_fixes.fix_products import update_all_products
from auto_fixes.fix_clothing import update_all_clothing
from utils.validators import *
from utils.headers import *

def display_results(title: str, errors: list[str]):
    if errors: 
        expander_title = f"{title} — {len(errors)} issue(s)"
        with st.expander(expander_title, expanded=False):
            for err in errors:
                st.markdown(f"- {err}")
    else:
        success_msg = ERROR_TYPES.get(title, f"{title} passed all checks.")
        st.success(success_msg)



st.title("New Product File Validation")
file_type = st.selectbox("Select File Type", ["Product", "Clothing", "Price Amendment"])

# File uploads
new_file = st.file_uploader(f"Upload New {file_type} File", type=["xlsx", "csv"])
# full_list_file = st.file_uploader("Upload PLU Active List", type=["xlsx", "csv"])
full_list_file = "1_Spreadsheets/CodesList.csv"

# Proceed only if both files uploaded
if file_type == "Product" and new_file and full_list_file:

# Step 1: Read and normalize new product file for auto fixes ---------
    try:
        expected_headers = [name for sublist in PRODUCT_HEADER_MAP.values() for name in sublist]
        header_row = detect_header_row(new_file, expected_headers)
        df = pd.read_excel(new_file, header=header_row)
        df.columns = [normalize_header(c) for c in df.columns]

        missing = check_missing_headers(df, PRODUCT_HEADER_MAP)                         # Check missing columns
        if not missing:
            st.success(f"All expected columns found in new file.")
        
    # Keep track of unrecognized header names
        unrecognized = unexpected_headers(df, PRODUCT_HEADER_MAP)
        if unrecognized:
            st.info(f"Unrecognized columns in file: {', '.join(unrecognized)}")

    # Apply auto-changes
        df, auto_changes = update_all_products(df)                       

    except Exception as e:
        st.error(f"Error reading or fixing new product file: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
                st.download_button(
                    label="Upload Templates",
                    data=file,
                    file_name="Upload Template Types.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        st.stop()

# Step 2: Load as Product class objects ----------
    try:
        products, messages = load_products(df) # was new file
        missing = []
        for message, type in messages:
            if type == "alert":
                st.success(message)
            elif type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in new file upload.")


    except Exception as e:
        st.error(f"Error loading new product file into Product objects: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
                st.download_button(
                    label="Upload Templates",
                    data=file,
                    file_name="Upload Template Types.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        st.stop()


# Step 3: Load PLU, Barcode list ---------
    try:
        # full_list_df = pd.read_excel(full_list_file)
        full_list_df = pd.read_csv(full_list_file)
        print(full_list_df.head(5))
        full_list_df.columns = [normalize_header(column) for column in full_list_df.columns]
        full_list_barcode, message, type = read_column(full_list_df, PRODUCT_HEADER_MAP["barcode"], used_columns=None)
        full_list_plu, message, type = read_column(full_list_df, PRODUCT_HEADER_MAP["plu_code"], used_columns=None)
    
        missing = []
        if message:
            if type == "alert":
                st.success(message)
            elif type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in full list upload.")

    except KeyError as e:
        st.error(f"Missing PLU column in full list: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading PLU Active List: {e}")
        st.stop()
    

# Error collection ---------
# duplicate_plu_dict = check_duplicates(products, all_plu)
    duplicate_plu_dict = check_duplicates(products, full_list_plu, "plu_code")
    duplicate_plu_errors = [
        f"Line: {line + 2} \u00A0\u00A0|\u00A0\u00A0 Product {plu} is already in the system."  # +2 to match Excel row (header + 0-indexed)
        for plu, line in duplicate_plu_dict.items()
    ]
    internal_duplicates = check_internal_duplicates(products, "plu_code")
    prod_barcode__internal_errors = duplicate_internal_barcodes(products, "plu_code")
    full_prod_barcode_errors = check_duplicates(products, full_list_barcode, "barcode")
    plu_in_barcodes = check_duplicates(products, full_list_barcode, "plu_code")
    barcodes_in_plu = check_duplicates(products, full_list_plu, "barcode")
    plu_errors = []
    prod_bad_char_errors = []
    
    

# Check all products and store in proper lists
    for product in products:
        if (e := product.plu_len()):
            plu_errors.append(e)
        
# Display errors
    display_results("Duplicate PLU Code Errors", duplicate_plu_errors)
    display_results("Duplicate PLUs Within Uploaded File", internal_duplicates)
    display_results("PLU Code Length Errors", plu_errors)
    display_results("Unusable Character Errors", prod_bad_char_errors)
    display_results("Duplicate Barcode Within New Upload", prod_barcode__internal_errors)
    display_results("Duplicate Barcodes In Database", full_prod_barcode_errors)
    display_results("Duplicate PLU's Used As Existing Barcodes", plu_in_barcodes)
    display_results("Duplicate Barcodes Used As Existing PLU's", barcodes_in_plu)


# If no errors
    if not any([duplicate_plu_errors, internal_duplicates, plu_errors, 
                 prod_bad_char_errors, 
                prod_barcode__internal_errors, full_prod_barcode_errors, 
                plu_in_barcodes, barcodes_in_plu]):
        st.success("All checks passed. File is ready for upload.")

    if any(auto_changes.values()):
        st.write("\n")
        st.title("Automatically Fixed Errors:")

        for category, changes in auto_changes.items():
            if changes:
                with st.expander(f"{category} ({len(changes)} fixes)", expanded=False):
                    for change in changes:
                        st.markdown(f"- {change}")

        # Convert to Excel in memory
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(
            label="Download Fixed Version",
            data=buffer.getvalue(),
            file_name= f"Fixed-{new_file.name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.title("No Auto-fixes Found")



elif file_type == "Clothing" and new_file and full_list_file:
# Step 1: Read and normalize new clothing file for auto fixes ---------

    try:
        expected_headers = [name for sublist in CLOTHING_HEADER_MAP.values() for name in sublist]
        header_row = detect_header_row(new_file, expected_headers)
        df = pd.read_excel(new_file, header=header_row)
        df.columns = [normalize_header(c) for c in df.columns]

        missing = check_missing_headers(df, CLOTHING_HEADER_MAP)                         # Check missing columns
        if missing:
            st.warning(f"Columns not found in new file: {', '.join(missing)}")
        else:
            st.success(f"All expected columns found in new file.")
        
    # Keep track of unrecognized header names
        unrecognized = unexpected_headers(df, CLOTHING_HEADER_MAP)
        if unrecognized:
            st.info(f"Unrecognized columns in file: {', '.join(unrecognized)}")

    # Apply auto fixes
        df, auto_changes = update_all_clothing(df)         
    except Exception as e:
        st.error(f"Error reading or fixing new clothing file: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
            st.download_button(
                label="Upload Templates",
                data=file,
                file_name="Upload Template Types.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.stop()

# Step 2: Load as Product class objects ----------
    try:
        clothes, messages = load_clothing(df)
        for message, type, in messages:
            if type == "alert":
                st.success(message)
            elif type == "error":
                st.error(message)

    except Exception as e:
        st.error(f"Error loading new clothing file into Clothing objects: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
            st.download_button(
                label="Upload Templates",
                data=file,
                file_name="Upload Template Types.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.stop()

# Step 3: Load Clothing list ---------
    try:
        full_list_df = pd.read_excel(full_list_file)
        full_list_df.columns = [normalize_header(c) for c in full_list_df.columns]
        full_list_barcode, message, type = read_column(full_list_df, CLOTHING_HEADER_MAP["barcode"])
        full_list_df, message, type = read_column(full_list_df, CLOTHING_HEADER_MAP["style_code"])

        if message:
            if type == "alert":
                st.success(message)
            elif type == "error":
                st.error(message)

    except KeyError as e:
        st.error(f"Missing Style Code column in full items list: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading full items list: {e}")
        st.stop()


    duplicate_styles = check_duplicates(clothes, full_list_df, "style_code")
    duplicate_style_errors = [
        f"Line: {line + 2} \u00A0\u00A0|\u00A0\u00A0 Item {style_code} is already in the system."  # +2 to match Excel row (header + 0-indexed)
        for style_code, line in duplicate_styles.items()
    ]
    internal_duplicates = check_clothing_duplicates(clothes)
    clothing_barcode_errors = duplicate_internal_barcodes(clothes, "style_code")
    style_code_in_barcodes = check_duplicates(clothes, full_list_barcode, "style_code")
    barcodes_in_style_code = check_duplicates(clothes, full_list_df, "barcode")
    style_len_errors = []
    clothing_bad_char_errors =[]

    

# Check all items and store in proper lists
    for item in clothes:
        if (e := item.style_len()):
            style_len_errors.append(e)



# Display Errors
    display_results("All Duplicate Style Code Code Errors", duplicate_style_errors)
    display_results("Duplicate Style Codes Within Uploaded File", internal_duplicates)
    display_results("All Style Code Length Errors", style_len_errors)
    display_results("All Unusable Character Errors", clothing_bad_char_errors)
    display_results("All Duplicate Barcode Errors", clothing_barcode_errors)
    display_results("Duplicate Style Codes Used As Existing Barcodes", style_code_in_barcodes)
    display_results("Duplicate Barcodes Used As Existing Style Codes", barcodes_in_style_code)


# If no errors
    if not any([duplicate_style_errors, internal_duplicates, style_len_errors, 
    clothing_bad_char_errors, clothing_barcode_errors, style_code_in_barcodes, barcodes_in_style_code]):
        st.success("All checks passed. File is ready for upload.")

# Auto fixing ------------------
    if any(auto_changes.values()):
        st.write("\n")
        st.title("Automatically Fixed Errors:")

        for category, changes in auto_changes.items():
            if changes:
                with st.expander(f"{category} ({len(changes)} fixes)", expanded=False):
                    for change in changes:
                        st.markdown(f"- {change}")

        # Convert to Excel in memory
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(
            label="Download Fixed Version",
            data=buffer.getvalue(),
            file_name= f"Fixed-{new_file.name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.title("No Auto-fixes Found")



elif file_type == "Price Amendment" and new_file and full_list_file:

    # # Read new file
    # df = pd.read_excel(new_file)
    # df.columns = [col.strip().lower().replace(" ", "") for col in df.columns]  # Optional: normalize columns
    # products, messages = load_products(df)

    # # Read full list
    # full_list_df = pd.read_excel(full_list_file)
    # full_list_df.columns = [normalize_header(column) for column in full_list_df.columns]
    # full_list_df, message, type = read_column(full_list_df, PRODUCT_HEADER_MAP["plu_code"])

    try:
            expected_headers = [name for sublist in PRODUCT_HEADER_MAP.values() for name in sublist]
            header_row = detect_header_row(new_file, expected_headers)
            df = pd.read_excel(new_file, header=header_row)
            df.columns = [normalize_header(c) for c in df.columns]

            missing = check_missing_headers(df, PRODUCT_HEADER_MAP)                         # Check missing columns
            if not missing:
            #     st.warning(f"Columns not found in new file: {','.join(missing)}")
            # else:
                st.success(f"All expected columns found in new file.")
            
        # Keep track of unrecognized header names
            recognized = set()
            for alias_list in PRODUCT_HEADER_MAP.values():
                recognized.update([normalize_header(h) for h in alias_list])

            unrecognized = [col for col in df.columns if col not in recognized]
            if unrecognized:
                st.info(f"Unrecognized columns in file: {', '.join(unrecognized)}")

        # # Apply auto-changes
        #     df, auto_changes = update_all_products(df)                       

    except Exception as e:
        st.error(f"Error reading or fixing new product file: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
            st.download_button(
                label="Upload Templates",
                data=file,
                file_name="Upload Template Types.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.stop()

    # Step 2: Load as Product class objects ----------
    try:
        products, messages = load_products(df) # was new file
        missing = []
        for message, type in messages:
            if type == "alert":
                st.success(message)
            elif type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in new file upload.")


    except Exception as e:
        st.error(f"Error loading new product file into Product objects: {e}. Excel format may be incorrect")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
            st.download_button(
                label="Upload Templates",
                data=file,
                file_name="Upload Template Types.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.stop()

    # Step 3: Load PLU list ---------
    try:
        full_list_df = pd.read_excel(full_list_file)
        full_list_df.columns = [normalize_header(column) for column in full_list_df.columns]
        full_list_df, message, type = read_column(full_list_df, PRODUCT_HEADER_MAP["plu_code"])


        missing = []
        if message:
            if type == "alert":
                st.success(message)
            elif type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in full list upload.")

    except KeyError as e:
        st.error(f"Missing PLU column in full list: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading PLU Active List: {e}")
        st.stop()
    


    results = check_exist(products, full_list_df, "plu_code")


    # if results:
    #     display_results("Non-amendable products", results)
    # else:


    if results: 
        st.header(f"Non-amendable products — {len(results)} issue(s)")
        for err in results:
            st.error(f"- {err}")
    else:
        st.header(f"Non-amendable products — 0 issue(s)")
        st.success("All products exist. File is ready for upload.")








