#!/usr/bin/python3.11
import csv
import sys
from datetime import datetime
from decimal import Decimal
from pprint import pprint

from datetime import datetime

def convert_date_format(date_str):
    """
    Convert date from 'Dec 3, 2024, 1:31:23 PM' format to '03.12.2024'.

    Parameters:
    date_str (str): The original date string to be converted.

    Returns:
    str: The formatted date string.
    """
    # Define the input and output formats
    input_format = "%b %d, %Y, %I:%M:%S %p"
    output_format = "%d.%m.%Y"

    # Parse the input string and format it
    date_obj = datetime.strptime(date_str, input_format)
    return date_obj.strftime(output_format)


def process_trade(file_path, option):
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)  # Skip the header row
        rows = list(csvreader)  # Load all rows
        rows.reverse()  # Reverse the list so we start from the last line
        my_data = {}
        total_fees = Decimal('0')
        total_quantity = Decimal('0')
        total_interest = Decimal('0')
        main_currency = "Not set"
        main_isin = "Not set"

                #Interest	Currency	Symbol Date/Time
        my_interest_headers = ["#Interest", "Currency", "Symbol", "Date/Time"]
        my_interest_row_format = "{:>10} {:>8} {:>15} {:>10}"
        my_headers = ["Comm/Fee", "Currency", "T.Price", "Symbol", "Quantity", "Date/Time", "Price*Quantity"]
        my_row_format = "{:>10} {:>10} {:>8} {:>15} {:>10} {:>10} {:>10}"
        header_row = my_row_format.format(*my_headers)
        header_interest_row = my_interest_row_format.format(*my_interest_headers)
        for row in rows:
            description = row[1]
            if "BUY" in description or "Service Fee" or "Interest PAID" in description:
                # Date, Description, Value, Price per share, Quantity of shares
                date = row[0]
                value = row[2]
                price_per_share = row[3]
                description_split = row[1].split()
                date_time = convert_date_format(date)
                isin = description_split[-1]
                if main_isin == isin or main_isin == "Not set":
                    next
                else:
                    print(f"ERROR we will not work with mor thay one ISIN {main_isin} == {isin}")
                    sys.exit(1)
                main_isin = isin
                if ( option == "buy" or option == "total" ) and "BUY" in description:
                    price_per_share = row[3].replace('£', '')
                    quantity = row[4]
                    total_quantity = Decimal(total_quantity) + Decimal(quantity)
                    currency = description_split[1]
                    total_price = Decimal(price_per_share) * Decimal(quantity)
                    my_row = [ 0, currency, price_per_share, isin, quantity, date_time, total_price]
                    my_current_row = my_row_format.format(*my_row)
                    #print(my_current_row)
                    if "buy" not in my_data:
                        my_data["buy"] = []
                    my_data["buy"].append(my_current_row)
                elif ( option == "fee" or option == "total" ) and "Service Fee" in description:
                    fee = row[2].replace('£', '')
                    total_fees += abs(Decimal(fee))
                    currency = description_split[3]
                    main_currency = currency
                    my_row = [ fee, currency, 0, isin, 0, date_time, 0]
                    my_current_row = my_row_format.format(*my_row)
                    #print(my_current_row)
                    if "fee" not in my_data:
                        my_data["fee"] = []
                    my_data["fee"].append(my_current_row)
                elif ( option == "interest" or option == "total" ) and "Interest PAID" in description:
                    interest = row[2].replace('£', '')
                    total_interest += abs(Decimal(interest))
                    currency = description_split[2]
                    main_currency = currency
                    my_row = [ interest, currency, isin, date_time]
                    my_current_row = my_interest_row_format.format(*my_row)
                    #print(my_current_row)
                    if "interest" not in my_data:
                        my_data["interest"] = []
                    my_data["interest"].append(my_current_row)
            else:
                print(f"ERROR: The csv cnatins rows that we do not handle:{description}")
                sys.exit(1)
        if option == "buy" or option == "total" :
            print("-" * len(header_row))
            print(header_row)
            for item in my_data["buy"]:
                print(item)
            print("-" * len(header_row))
            print(f"Total BUY Quantity: {total_quantity} {isin}")
            print("-" * len(header_row))

        if option == "fee" or option == "total" :
            if option == "fee":
                print("-" * len(header_row))
                print(header_row)
                for item in my_data["fee"]:
                    print(item)
            print("-" * len(header_row))
            print(f"Total fees: {total_fees} {main_currency}")
            print("-" * len(header_row))
        if option == "interest" or option == "total" :
            if option == "interest":
                print("-" * len(header_interest_row))
                print(header_interest_row)
                for item in my_data["interest"]:
                    print(item)
            print("-" * len(header_interest_row))
            print(f"Total interests recived: {total_interest} {main_currency} {isin}")
            if option == "total":
                print(f"Total profit(Interests - fees): {total_interest - total_fees} {main_currency} {isin}")
            print("-" * len(header_interest_row))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: script.py <csv_file> <option>")
        print("Options:")
        print("  -b, --buy Process trades (BUY or Service Fee)")
        print("  -i, --interest Process interests")
        print("  -f, --fee Process fees")
        print("  -t, --total Process all and show tatal + buys")
        sys.exit(1)

    file_path = sys.argv[1]
    option = sys.argv[2]

    if option in ['-b', '--buy']:
        process_trade(file_path, "buy")
    elif option in ['-f', '--fee']:
        process_trade(file_path, "fee")
    elif option in ['-i', '--interest']:
        process_trade(file_path, "interest")
    elif option in ['-t', '--total']:
        process_trade(file_path, "total")
    else:
        print("Invalid option. Use -t or --trade, or -i or --interests.")

