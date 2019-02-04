import os

import xlrd
import pandas as pd

from src.constants import (
    PARENT_BOM,
    COMPONENT_BOM,
    SHEET_NAME_ZSALDASH,
    HEADER_INDEX_ZSALDASH,
)

from src.process_df import process_df


def modify_sales(bom_df, input_dir, output_dir):
    files = [
        f
        for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f)) and SHEET_NAME_ZSALDASH in f
    ]

    if len(files) == 0:
        print("No ZSALDASH files found!!!")
        return

    parent_to_product_mapping = bom_df.groupby([PARENT_BOM])[COMPONENT_BOM].unique()

    for f in files:
        print(f"Reading {f}")
        try:
            df = pd.read_excel(
                os.path.join(input_dir, f),
                sheet_name=SHEET_NAME_ZSALDASH,
                header=HEADER_INDEX_ZSALDASH,
                na_values=[" "],
            )

            print(f"Processing {f}")
            df = process_df(df, bom_df, parent_to_product_mapping, "sales")

            print(f"Writing {f}")
            df.to_excel(
                os.path.join(output_dir, f), sheet_name=SHEET_NAME_ZSALDASH, index=False
            )
        except xlrd.XLRDError as e:
            print(f"Unable to process {f}: {e}")
