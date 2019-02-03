import os

import pandas as pd


def read_bom(directory):
    files = [
        f
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and "BOM" in f
    ]

    if len(files) == 0:
        print("No BOM files found!!!")
        exit()

    if len(files) >= 2:
        print(f"Multiple BOM files found: {files}")
        exit()

    print(f"Reading {files[0]} for BOM")
    df_list = pd.read_excel(os.path.join(directory, files[0]), sheet_name=None)

    valid_sheets = [
        k
        for k, df in df_list.items()
        if "Parent Product" in df and "Component" in df and "Link Quantity" in df
    ]

    if len(valid_sheets) == 0:
        print(f"Could not find any sheet in <{files[0]}> which contains "
              f"Parent Product, Component, and Link Quantity")

    if len(valid_sheets) >= 2:
        print(f"Found multiple sheets in <{files[0]}> containing "
              f"Parent Product, Component, and Link Quantity: {valid_sheets}")

    print(f"Using Sheet: {valid_sheets[0]} for BOM")
    bom_df = df_list[valid_sheets[0]]
    bom_df["Link Quantity"] = bom_df["Link Quantity"].astype("float")

    for c in ["Parent Product", "Component"]:
        bom_df[c] = bom_df[c].apply(str)

    return bom_df


def make_component_to_product_mapping(bom_df):
    mapping = bom_df.groupby(['Component'])['Parent Product'].unique().to_dict()
    return {k: list(v) for k, v in mapping.items()}
