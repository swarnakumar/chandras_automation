import pandas as pd

from src.constants import ROLLUP_PRODUCT, KIT_INDICATOR
from src.constants import PARENT_BOM, COMPONENT_BOM, LINK_QUANTITY_BOM
from src.constants import (
    ORDER_NUMBER_ZOPNDASH,
    PRODUCT_ZOPNDASH,
    ORDER_QUANTITY_ZOPNDASH,
    SALES_ZOPNDASH,
)
from src.constants import (
    ORDER_NUMBER_ZSALDASH,
    PRODUCT_ZSALDASH,
    ORDER_QUANTITY_ZSALDASH,
    SALES_ZSALDASH,
)


def process_df(df, bom_df, parent_to_product_mapping, file_type):
    if file_type == "sales":
        order_number = ORDER_NUMBER_ZSALDASH
        product_id = PRODUCT_ZSALDASH
        order_qty = ORDER_QUANTITY_ZSALDASH
        sales = SALES_ZSALDASH
    else:
        order_number = ORDER_NUMBER_ZOPNDASH
        product_id = PRODUCT_ZOPNDASH
        order_qty = ORDER_QUANTITY_ZOPNDASH
        sales = SALES_ZOPNDASH

    df = df[~(df[order_number].isnull())]
    df[order_qty] = df[order_qty].apply(float)

    df[product_id] = df[product_id].apply(str)

    def grouper(row):
        return get_parent_product(
            row, parent_to_product_mapping, bom_df, product_id, order_qty, sales
        )

    def get_kit_indicator(row):
        if row[product_id] == row[ROLLUP_PRODUCT]:
            if row[product_id] in parent_to_product_mapping:
                return "Parent"
            else:
                return "Independent"
        else:
            return "Component"

    rollup = (
        df.groupby(order_number)
        .apply(grouper)
        .reset_index()
        .set_index("level_1")
        .drop([order_number], axis=1)
    )
    rollup.index.names = df.index.names
    df[ROLLUP_PRODUCT] = rollup[ROLLUP_PRODUCT]

    df[KIT_INDICATOR] = df.apply(get_kit_indicator, axis=1)
    return df


def get_parent_product(
    invoice, parent_to_product_mapping, bom_df, product_name, order_quantity, sales
):
    parents = [p for p in invoice[product_name] if p in parent_to_product_mapping]
    if not parents:
        return pd.Series(
            invoice[product_name], index=invoice.index, name=ROLLUP_PRODUCT
        )

    parent_rows = invoice[invoice[product_name].isin(parents)].index
    parent_column = pd.Series(None, index=invoice.index, name=ROLLUP_PRODUCT)

    parent_column.loc[parent_rows] = invoice.loc[parent_rows, product_name]

    for parent_ind in parent_rows:
        parent_row = invoice.loc[parent_ind]
        p = parent_row[product_name]
        parent_qty = parent_row[order_quantity]
        parent_bom = bom_df[bom_df[PARENT_BOM] == p]
        bom_component_link_qty = parent_bom.set_index(COMPONENT_BOM)[LINK_QUANTITY_BOM]

        expected_qty = (bom_component_link_qty * parent_qty).to_dict()

        zero_rows = invoice[(invoice[sales] == 0) & (parent_column.isnull())].index

        mapped = []

        for ind in zero_rows:
            row = invoice.loc[ind]
            comp = row[product_name]
            if comp not in mapped and row[order_quantity] == expected_qty.get(comp, 0):
                parent_column.loc[ind] = p
                mapped.append(row[product_name])

    null_rows = parent_column[parent_column.isnull()].index
    parent_column.loc[null_rows] = invoice.loc[null_rows, product_name]

    return parent_column
