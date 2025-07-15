import streamlit as st


class Price_Amend:
    def __init__(self, code, description, main_supplier, cost_price, rrp, sell_price, stg_price, idx=None):
        self.plu_code = code
        self.description = description
        self.main_supplier = main_supplier
        self.cost = cost_price
        self.rrp = rrp
        self.sell_price = sell_price
        self.stg_price = stg_price
        self.excel_line = idx


    def __repr__(self):
        return f"Product {self.plu_code}: {self.description}"


    def __str__(self):
        return f"Product: {self.plu_code} | {self.description}"


    def plu_len(self):
        """ Checks if any products have a PLU Code length over 15"""
        if len(str(self.plu_code)) > 15:
            return f"Line {self.excel_line} \u00A0\u00A0|\u00A0\u00A0 Product: {self.plu_code} has PLU Code length of {len(str(self.plu_code))}. Must be under 15."
            # print(f"Product: {self.plu_code} has PLU Code length of {len(str(self.plu_code))}. Must be under 15.")
            # st.write(f"Product: {self.plu_code} has PLU Code length of {len(str(self.plu_code))}. Must be under 15.")

        