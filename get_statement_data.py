#!/usr/bin/env python3
import sys
from datetime import datetime
import argparse
import shutil
import copy

# from pprint import pprint
from Trades import Parsestatementdatacsv
terminal_width = shutil.get_terminal_size().columns


def get_trade_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    all_key_val = []
    keys_to_print = ['Comm/Fee', 'Currency', 'T. Price', 'Symbol', 'Quantity', 'Date/Time', 'Price * Quantity',
                     "Date/Time_For_sort"]

    for el in data['Order']:
        for order_val in data['Order'][el]:
            original_date = datetime.strptime(order_val['Date/Time'], "%Y-%m-%d, %H:%M:%S")
            order_val['Date/Time_For_sort'] = order_val['Date/Time']
            order_val['Date/Time'] = original_date.strftime("%d.%m.%Y")
            order_val['Price * Quantity'] = str(float(order_val['T. Price']) * float(order_val['Quantity']))
            keys_val = ' '.join(order_val[key] for key in keys_to_print if key in order_val)
            all_key_val.append(keys_val)
    sorted_all_key_val = sorted(all_key_val, key=lambda x: datetime.strptime(x.split()[-2], "%Y-%m-%d,"))
    original_aray_witout_sort_date = [' '.join(string.split()[:-2]) for string in sorted_all_key_val]
    print(' '.join(key for key in keys_to_print))
    print(' \n'.join(key for key in original_aray_witout_sort_date))
    print('-' * terminal_width)


def get_dividend_tax_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    all_pyed_tax = 0
    all_tax_count = 0
    all_key_val = []
    keys_to_print = ['Date', 'Currency', 'ISIN', 'Amount']
    for tiker in data['Withholding Tax']:
        for dividend_tax_val in data['Withholding Tax'][tiker]:
            original_date = datetime.strptime(dividend_tax_val['Date'], "%Y-%m-%d")
            dividend_tax_val['Date'] = original_date.strftime("%d.%m.%Y")
            keys_val = ' '.join(dividend_tax_val[key] for key in keys_to_print if key in dividend_tax_val)
            all_key_val.append(keys_val)
            all_pyed_tax = float(all_pyed_tax) + float(dividend_tax_val['Amount'])
            all_tax_count += 1
    print(' '.join(key for key in keys_to_print))
    print(' \n'.join(key for key in all_key_val))
    print("All tax: " + str(all_pyed_tax))
    print("Dividend tax count: " + str(all_tax_count))
    print('-' * terminal_width)


def get_dividend_and_dividend_tax_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    all_dividend_received = 0
    all_dividend_count = 0
    all_pyed_tax = 0
    all_tax_count = 0
    all_key_val = []
    keys_to_print = ['Date', 'Currency', 'ISIN', 'Amount', 'Tax_Amount', 'Date/Time_For_sort']

    for tiker in data['Dividends']:
        for dividend_and_tax_val in data['Dividends'][tiker]:
            if tiker in data['Withholding Tax']:
                tax_dividend_set = 0
                for tax_tiker_data in data['Withholding Tax'][tiker]:
                    if dividend_and_tax_val['Date'] == tax_tiker_data['Date']:
                        dividend_and_tax_val['Tax_Amount'] = tax_tiker_data['Amount']
                        all_pyed_tax = float(all_pyed_tax) + float(tax_tiker_data['Amount'])
                        tax_dividend_set = 1
                        all_tax_count += 1
                if tax_dividend_set == 0:
                    dividend_and_tax_val['Tax_Amount'] = "0"
                    all_tax_count += 1
            else:
                dividend_and_tax_val['Tax_Amount'] = "0"
            dividend_and_tax_val['Date/Time_For_sort'] = dividend_and_tax_val['Date']
            original_date = datetime.strptime(dividend_and_tax_val['Date'], "%Y-%m-%d")
            dividend_and_tax_val['Date'] = original_date.strftime("%d.%m.%Y")
            keys_val = ' '.join(dividend_and_tax_val[key] for key in keys_to_print if key in dividend_and_tax_val)
            all_key_val.append(keys_val)
            all_dividend_received = float(all_dividend_received) + float(dividend_and_tax_val['Amount'])
            all_dividend_count += 1

    sorted_all_key_val = sorted(all_key_val, key=lambda x: datetime.strptime(x.split()[-1], "%Y-%m-%d"))
    original_aray_witout_sort_date = [' '.join(string.split()[:-1]) for string in sorted_all_key_val]
    print(' '.join(key for key in keys_to_print))
    print(' \n'.join(key for key in original_aray_witout_sort_date))
    print("All dividend received USD: " + str(all_dividend_received))
    print("All tax: " + str(all_pyed_tax))
    print("Dividend count: " + str(all_dividend_count))
    print("Dividend tax count: " + str(all_tax_count))
    print('-' * terminal_width)


def get_dividend_tax_total_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    print("Withholding Tax Total USD: " + data['Withholding Tax Total'])
    print("Withholding Tax Total EUR: " + data['Withholding Tax Total in EUR'])
    print('-' * terminal_width)


def get_dividend_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    all_dividend_received = 0
    all_dividend_count = 0
    all_key_val = []

    keys_to_print = ['Date', 'Currency', 'ISIN', 'Amount']
    for tiker in data['Dividends']:
        for dividend_val in data['Dividends'][tiker]:
            original_date = datetime.strptime(dividend_val['Date'], "%Y-%m-%d")
            dividend_val['Date'] = original_date.strftime("%d.%m.%Y")
            keys_val = ' '.join(dividend_val[key] for key in keys_to_print if key in dividend_val)
            all_key_val.append(keys_val)
            all_dividend_received = float(all_dividend_received) + float(dividend_val['Amount'])
            all_dividend_count += 1
    print(' '.join(key for key in keys_to_print))
    print(' \n'.join(key for key in all_key_val))
    print("All dividend received USD: " + str(all_dividend_received))
    print("Dividend count: " + str(all_dividend_count))
    print('-' * terminal_width)


def get_dividend_total_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    print("Dividends Total USD: " + data['Dividends Total USD'])
    print("Dividends Total EUR: " + data['Dividends Total in EUR'])
    print('-' * terminal_width)


def get_cash_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    for cash_info, cash_info_array in data['Cash Report'].items():
        if cash_info == 'Starting Cash' or \
                cash_info == 'Ending Settled Cash' or \
                cash_info == 'Ending Cash':
            continue
        values = {cash_info: []}
        for el in cash_info_array:
            all_array_items = '\t'
            for key1, value1 in el.items():
                if key1 != "" and value1 != "":
                    if cash_info != value1:
                        if key1 == 'Currency':
                            all_array_items = all_array_items + f': {value1} '
                        else:
                            all_array_items = all_array_items + f'{key1}: {value1} '
            values[cash_info].append(all_array_items)
        print(cash_info)
        print(' \n'.join(element for element in values[cash_info]))
        print('-' * terminal_width)


def get_open_positions_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    all_key_val = []
    keys_to_print = ['Symbol', 'Quantity', 'Cost Price', 'Value']

    for open_val in data['Open Positions']['Summary']:
        keys_val = '\t'.join(open_val[key] for key in keys_to_print if key in open_val)
        all_key_val.append(keys_val)
    print('\t'.join(key for key in keys_to_print))
    print(' \n'.join(key for key in sorted(all_key_val)))
    print('-' * terminal_width)


def run_get_info():
    parser = argparse.ArgumentParser(description='Get trade info for statement.')
    parser.add_argument('file_name', help='Statement csv file with all possible information')
    parser.add_argument('-c', '--cash-report', action='store_true', help='List all cash information.')
    parser.add_argument('-b', '--trade-report', action='store_true', help='List all trade information.')
    parser.add_argument('-d', '--dividend-report', action='store_true', help='List all dividend information.')
    parser.add_argument('-dt', '--dividend-total-report', action='store_true',
                        help='List all dividend total information.')
    parser.add_argument('-x', '--dividend-tax-report', action='store_true', help='List all dividend tax information.')
    parser.add_argument('-dxt', '--dividend-tax-total-report', action='store_true',
                        help='List all dividend tax total information.')
    parser.add_argument('-dx', '--dividend-and-dividend-tax-report', action='store_true',
                        help='List all dividend and dividendtax information.')
    parser.add_argument('-o', '--open-positions-report', action='store_true',
                        help='List all open positions information.')

    args = parser.parse_args()
    csv_reader = Parsestatementdatacsv(args.file_name)
    csv_data = csv_reader.read_csv
    my_args_true = {}
    if parser._option_string_actions:
        my_parsed_string_options = parser._option_string_actions
    else:
        my_parsed_string_options = {}
    for action in my_parsed_string_options:
        action_str = str(my_parsed_string_options[action])
        action_array = action_str.split()
        if 'const=True' in action_array[4]:
            split_string = action_array[2].split("'")
            if getattr(args, split_string[1]):
                my_args_true[action] = split_string[1]

    for arg in sys.argv:
        if arg in my_args_true:
            function_to_call = 'get_' + my_args_true[arg]
            globals()[function_to_call](csv_data)


run_get_info()
