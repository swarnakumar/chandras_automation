import os

import xlrd
import pandas as pd

from src.constants import ROLLUP_PRODUCT, KIT_INDICATOR
from src.constants import (
    PRODUCT_ZSALDASH as PRODUCT_ZSALDASH,
    ORDER_NUMBER_ZSALDASH as ORDER_NUMBER_ZSALDASH,
    ORDER_QUANTITY_ZSALDASH as ORDER_QUANTITY_ZSALDASH,
)

from src.parent_product import get_parent_product_sales


def modify_sales(bom_df, input_dir, output_dir):
    files = [
        f
        for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f)) and "ZSALDASH" in f
    ]

    if len(files) == 0:
        print("No ZSALDASH files found!!!")
        return

    parent_to_product_mapping = bom_df.groupby(["Parent Product"])["Component"].unique()

    def get_kit_indicator(row):
        if row[PRODUCT_ZSALDASH] == row[ROLLUP_PRODUCT]:
            if row[PRODUCT_ZSALDASH] in parent_to_product_mapping:
                return "Parent"
            else:
                return "Independent"
        else:
            return "Component"

    for f in files:
        print(f"Reading {f}")
        try:
            df = pd.read_excel(
                os.path.join(input_dir, f),
                sheet_name="ZSALDASH",
                header=4,
                na_values=[" "],
            )

            df = df[~(df["OrderNumber"].isnull())]
            df[ORDER_QUANTITY_ZSALDASH] = df[ORDER_QUANTITY_ZSALDASH].apply(float)

            df[PRODUCT_ZSALDASH] = df[PRODUCT_ZSALDASH].apply(str)

            print(f"Adding Rollup for {f}")

            rollup = (
                df.groupby(ORDER_NUMBER_ZSALDASH)
                .apply(
                    lambda x: get_parent_product_sales(
                        x, parent_to_product_mapping, bom_df
                    )
                )
                .reset_index()
                .set_index("level_1")
                .drop([ORDER_NUMBER_ZSALDASH], axis=1)
            )
            rollup.index.names = df.index.names
            df[ROLLUP_PRODUCT] = rollup[ROLLUP_PRODUCT]

            print(f"Adding Kit Indicator for {f}")
            df[KIT_INDICATOR] = df.apply(get_kit_indicator, axis=1)

            print(f"Writing {f}")
            df.to_excel(os.path.join(output_dir, f), sheet_name="ZSALDASH", index=False)
        except xlrd.XLRDError as e:
            print(f"Unable to process {f}: {e}")
