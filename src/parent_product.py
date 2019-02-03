import pandas as pd

from src.constants import ROLLUP_PRODUCT
from src.constants import PRODUCT_ZOPNDASH, ORDER_QUANTITY_ZOPNDASH, SALES_ZOPNDASH
from src.constants import PRODUCT_ZSALDASH, ORDER_QUANTITY_ZSALDASH, SALES_ZSALDASH
from src.constants import PARENT_BOM, COMPONENT_BOM, LINK_QUANTITY_BOM


def get_parent_product_open_orders(invoice, parent_to_product_mapping, bom_df):
    return get_parent_product(
        invoice,
        parent_to_product_mapping,
        bom_df,
        PRODUCT_ZOPNDASH,
        ORDER_QUANTITY_ZOPNDASH,
        SALES_ZOPNDASH,
    )


def get_parent_product_sales(invoice, parent_to_product_mapping, bom_df):
    return get_parent_product(
        invoice,
        parent_to_product_mapping,
        bom_df,
        PRODUCT_ZSALDASH,
        ORDER_QUANTITY_ZSALDASH,
        SALES_ZSALDASH,
    )


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
