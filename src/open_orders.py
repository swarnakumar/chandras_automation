import os

import xlrd
import pandas as pd

from src.constants import ROLLUP_PRODUCT, KIT_INDICATOR
from src.constants import (
    PRODUCT_ZOPNDASH,
    ORDER_NUMBER_ZOPNDASH,
    ORDER_QUANTITY_ZOPNDASH,
)

from src.parent_product import get_parent_product_open_orders


def modify_open_orders(bom_df, input_dir, output_dir):
    files = [
        f
        for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f)) and "ZOPNDASH" in f
    ]

    if len(files) == 0:
        print("No ZOPNDASH files found!!!")
        return

    parent_to_product_mapping = bom_df.groupby(["Parent Product"])["Component"].unique()

    def get_kit_indicator(row):
        if row[PRODUCT_ZOPNDASH] == row[ROLLUP_PRODUCT]:
            if row[PRODUCT_ZOPNDASH] in parent_to_product_mapping:
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
                sheet_name="ZOPNDASH",
                header=3,
                na_values=[" "],
            )

            df = df[~(df["OrderNumber"].isnull())]
            df[ORDER_QUANTITY_ZOPNDASH] = df[ORDER_QUANTITY_ZOPNDASH].apply(float)

            df[PRODUCT_ZOPNDASH] = df[PRODUCT_ZOPNDASH].apply(str)

            print(f"Processing {f}")

            rollup = (
                df.groupby(ORDER_NUMBER_ZOPNDASH)
                .apply(
                    lambda x: get_parent_product_open_orders(
                        x, parent_to_product_mapping, bom_df
                    )
                )
                .reset_index()
                .set_index("level_1")
                .drop([ORDER_NUMBER_ZOPNDASH], axis=1)
            )
            rollup.index.names = df.index.names
            df[ROLLUP_PRODUCT] = rollup[ROLLUP_PRODUCT]

            df[KIT_INDICATOR] = df.apply(get_kit_indicator, axis=1)

            print(f"Writing {f}")
            df.to_excel(os.path.join(output_dir, f), sheet_name="ZOPNDASH", index=False)
        except xlrd.XLRDError as e:
            print(f"Unable to process {f}: {e}")
