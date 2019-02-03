#! env/bin/python

import os
import sys
import datetime

from src.bom import read_bom
from src.open_orders import modify_open_orders
from src.sales import modify_sales


if __name__ == "__main__":
    args = sys.argv
    if len(args) <= 2:
        print("Both INPUT and OUTPUT Directory Names are required!!!")
        exit()

    input_directory = os.path.abspath(sys.argv[1])
    if not os.path.exists(input_directory):
        print(f"Invalid Directory: {input_directory}")
        exit()

    print(datetime.datetime.now(), 'Reading BOM')
    bom_df = read_bom(input_directory)

    output_directory = os.path.abspath(sys.argv[2])
    os.makedirs(output_directory, exist_ok=True)
    print(datetime.datetime.now(), 'Modifying Open Orders')
    modify_open_orders(bom_df, input_directory, output_directory)
    print(datetime.datetime.now(), 'Modifying Sales')
    modify_sales(bom_df, input_directory, output_directory)
    print(datetime.datetime.now(), 'Completed')
