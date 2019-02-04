import os

import xlrd
import pandas as pd

from src.constants import (
    PARENT_BOM,
    COMPONENT_BOM,
    SHEET_NAME_ZOPNDASH,
    HEADER_INDEX_ZOPNDASH,
    PRODUCT_ZOPNDASH,
    ORDER_NUMBER_ZOPNDASH,
    ORDER_QUANTITY_ZOPNDASH,
)

from src.process_df import process_df


def modify_open_orders(bom_df, input_dir, output_dir):
    files = [
        f
        for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f)) and SHEET_NAME_ZOPNDASH in f
    ]

    if len(files) == 0:
        print("No ZOPNDASH files found!!!")
        return

    parent_to_product_mapping = bom_df.groupby([PARENT_BOM])[COMPONENT_BOM].unique()

    for f in files:
        print(f"Reading {f}")
        try:
            df = pd.read_excel(
                os.path.join(input_dir, f),
                sheet_name=SHEET_NAME_ZOPNDASH,
                header=HEADER_INDEX_ZOPNDASH,
                na_values=[" "],
            )

            print(f"Processing {f}")
            df = process_df(df, bom_df, parent_to_product_mapping, "orders")

            df = df[~(df[ORDER_NUMBER_ZOPNDASH].isnull())]
            df[ORDER_QUANTITY_ZOPNDASH] = df[ORDER_QUANTITY_ZOPNDASH].apply(float)

            df[PRODUCT_ZOPNDASH] = df[PRODUCT_ZOPNDASH].apply(str)

            print(f"Writing {f}")
            df.to_excel(
                os.path.join(output_dir, f), sheet_name=SHEET_NAME_ZOPNDASH, index=False
            )
        except xlrd.XLRDError as e:
            print(f"Unable to process {f}: {e}")
