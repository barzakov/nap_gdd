#!/usr/bin/env python3
import sys
from datetime import datetime
import argparse
import shutil
import copy
from decimal import Decimal
import re


def _is_cash_dividend(desc: str) -> bool:
    if not desc:
        return False
    # match "cash div" with common truncations/dots at end (case-insensitive)
    return bool(re.search(r'cash\s+div\w{0,6}\.*\s*$', desc, re.IGNORECASE))


# from pprint import pprint
from Trades.utils import Parsestatementdatacsv
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
            order_val['Price * Quantity'] = str(Decimal(order_val['T. Price']) * Decimal(order_val['Quantity'].replace(",", "")))
            keys_val = ' '.join(order_val[key] for key in keys_to_print if key in order_val)
            all_key_val.append(keys_val)
    sorted_all_key_val = sorted(all_key_val, key=lambda x: datetime.strptime(x.split()[-2], "%Y-%m-%d,"))
    original_aray_without_sort_date = ['\t'.join(string.split()[:-2]) for string in sorted_all_key_val]
    keys_to_print.pop()
    print('\t'.join(key.replace(' ', '') for key in keys_to_print))
    print(' \n'.join(key for key in original_aray_without_sort_date))
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
            all_pyed_tax += Decimal(dividend_tax_val['Amount'])
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
                        all_pyed_tax += Decimal(tax_tiker_data['Amount'])
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
            all_dividend_received += Decimal(dividend_and_tax_val['Amount'])
            all_dividend_count += 1

    sorted_all_key_val = sorted(all_key_val, key=lambda x: datetime.strptime(x.split()[-1], "%Y-%m-%d"))
    original_aray_without_sort_date = ['\t'.join(string.split()[:-1]) for string in sorted_all_key_val]
    keys_to_print.pop()
    print('\t'.join(key for key in keys_to_print))
    print(' \n'.join(key for key in original_aray_without_sort_date))
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
            all_dividend_received += Decimal(dividend_val['Amount'])
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

    net_info_array = []
    for net_info in data['Net Asset Value']:
        for net_info_el in data['Net Asset Value'][net_info]:
            if 'Current Total' in net_info_el:
                net_info_array.append({net_info_el['Asset Class']: net_info_el['Current Total']})
            if 'Time Weighted Rate of Return' in net_info_el:
                net_info_array.append({'Time Weighted Rate of Return': net_info_el['Time Weighted Rate of Return']})
    print("Net Assets")
    for net_cash_info in net_info_array:
        for key, value in net_cash_info.items():
            print(f"\t{key}: {value}")
    print('-' * terminal_width)

    for cash_info, cash_info_array in data['Cash Report'].items():
        if cash_info == 'Ending Settled Cash':
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

    open_positions_symbols = [item.split('\t')[0] for item in all_key_val]
    list_set = set(open_positions_symbols)
    dict_keys = set()
    # Find last 4-digit year (robust for formats)
    period = data['Statement']['Period']
    end_year_match = re.search(r'(\d{4})(?!\d)', period)
    end_year = int(end_year_match.group(1)) if end_year_match else None
    if end_year <= 2024:
        dict_keys = set(data['Instrument Information'].keys())
    else:
        tiker_symol_to_use = 'Underlying'
        for key, value in data['Instrument Information'].items():
            if isinstance(value, dict) and tiker_symol_to_use in value:
    # DO not include Symols that Underlying tiker end with .OLD since ther and not used anymore
                if str(value[tiker_symol_to_use]).endswith('.OLD'):
                    continue  # Exclude this key
            dict_keys.add(key)
    # Symbols in list Open Positions but not dict Instrument Information
    missing_in_dict = sorted(list_set - dict_keys)
    # Keys in dict Instrument Information but not list Open Positions
    extra_in_dict = sorted(dict_keys - list_set)
    if missing_in_dict:
        print("\n!!!!!!!\nERROR; Symbols NOT in dict Instrument Information:", missing_in_dict, "\n!!!!!!!\n")
    if extra_in_dict:
        print("\n!!!!!!!\nERROR: EXTRA keys in dict Instrument Information (missing from list Open Positions) probably \
        Sell or Merged(Acquisition):", extra_in_dict, "\n!!!!!!!!\n")

    # New columns and data collection
    new_keys_to_print = ['Security ID', 'Quantity', 'Symbol', 'Underlying', 'Listing Exch', 'Type', 'Description', 'Cost Price', 'Value']
    rows = []
    for open_val in data['Open Positions']['Summary']:
        symbol = open_val['Symbol']
        if symbol in data['Instrument Information']:
            info = data['Instrument Information'][symbol]
            row = [
                info.get('Security ID', ''),
                open_val.get('Quantity', ''),
                symbol,
                info.get('Underlying', ''),
                info.get('Listing Exch', ''),
                info.get('Type', ''),
                info.get('Description', ''),
                open_val.get('Cost Price', ''),
                open_val.get('Value', '')
            ]
            rows.append(row)

    # Sort rows by Symbol (index 2)
    rows.sort(key=lambda r: r[2])

    # Calculate max widths for each column
    widths = [max(len(str(row[i])) for row in rows) if rows else 0 for i in range(len(new_keys_to_print))]
    header_widths = [max(widths[i], len(new_keys_to_print[i])) for i in range(len(new_keys_to_print))]

    # Print header
    header = '  '.join(f"{new_keys_to_print[i]:<{header_widths[i]}}" for i in range(len(new_keys_to_print)))
    print(header)

    # Print rows
    for row in rows:
        line = '  '.join(f"{str(row[i]):<{header_widths[i]}}" for i in range(len(row)))
        print(line)

    print('-' * terminal_width)


def get_forex_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    keys_to_print = ['Date/Time', 'Description', 'Quantity', 'Proceeds in EUR', 'Basis in EUR', 'Realized P/L in EUR']
    all_key_val = []
    for group_key in data.get('Forex', {}):
        for forex_entry in data['Forex'][group_key]:
            if 'Date/Time' in forex_entry:
                try:
                    original_date = datetime.strptime(forex_entry['Date/Time'], "%Y-%m-%d, %H:%M:%S")
                    forex_entry['Date/Time'] = original_date.strftime("%d.%m.%Y")
                except Exception:
                    # keep original if parse fails
                    pass
            keys_val = ' '.join(forex_entry[key] for key in keys_to_print if key in forex_entry)
            all_key_val.append(keys_val)
    print(' '.join(key for key in keys_to_print))
    if all_key_val:
        print(' \n'.join(key for key in all_key_val))
    else:
        print("(no forex rows found)")
    if 'Forex Total' in data:
        print("Forex Total: " + str(data['Forex Total']))
    print('-' * terminal_width)


def get_forex_dividend_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    rows = []
    for group_key in data.get('Forex', {}):
        for entry in data['Forex'][group_key]:
            desc = entry.get('Description', '')
            # only consider forex entries that are cash dividends (allow truncated endings)
            if not _is_cash_dividend(desc):
                continue
            qty = str(entry.get('Quantity', '')).strip()
            # only payouts (quantity not starting with '-')
            if qty.startswith('-'):
                continue
            date_raw = entry.get('Date/Time', entry.get('Date', ''))
            try:
                dt = datetime.strptime(date_raw, "%Y-%m-%d, %H:%M:%S")
            except Exception:
                try:
                    dt = datetime.strptime(date_raw, "%Y-%m-%d")
                except Exception:
                    dt = None
            date_out = dt.strftime("%d.%m.%Y") if dt else date_raw
            desc = entry.get('Description', '')
            # extract leading token like MSF(US5949181045) if present
            m = re.match(r'(^\S+\(\S+\))', desc)
            display = m.group(1) if m else desc
            in_eur = entry.get('Proceeds in EUR', '')
            # store parsed datetime plus formatted output so we can sort by date
            rows.append((dt, date_out, display, in_eur))

    # sort by parsed datetime (None goes last)
    rows_sorted = sorted(rows, key=lambda r: (0, r[0]) if r[0] else (1, ''))
    print("Date\tISIN\tIN_EUR")
    for r in rows_sorted:
        print(f"{r[1]}\t{r[2]}\t{r[3]}")
    print('-' * terminal_width)


def get_forex_dividend_tax_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    positives = []
    negatives_by_desc = {}
    for group_key in data.get('Forex', {}):
        for entry in data['Forex'][group_key]:
            desc = entry.get('Description', '')
            # only consider forex entries that are cash dividends (allow truncated endings)
            if not _is_cash_dividend(desc):
                continue
            qty = str(entry.get('Quantity', '')).strip()
            date_raw = entry.get('Date/Time', entry.get('Date', ''))
            try:
                dt = datetime.strptime(date_raw, "%Y-%m-%d, %H:%M:%S").date()
            except Exception:
                try:
                    dt = datetime.strptime(date_raw, "%Y-%m-%d").date()
                except Exception:
                    dt = None
            desc = entry.get('Description', '')
            m = re.match(r'(^\S+\(\S+\))', desc)
            display = m.group(1) if m else desc
            proceeds = entry.get('Proceeds in EUR', '')
            if qty.startswith('-'):
                negatives_by_desc.setdefault(display, []).append({'date': dt, 'proceeds': proceeds})
            else:
                positives.append({'date': dt, 'display': display, 'proceeds': proceeds})

    # sort positives by date ascending (None goes last) then match negatives
    positives_sorted = sorted(positives, key=lambda p: (0, p['date']) if p['date'] else (1, None))
    # match positives with negatives: exact date first, then ±1 day
    print("Date\tISIN\tIN_EUR\tTax_Amount_in_EUR")
    for p in positives_sorted:
        tax_value = ''
        negs = negatives_by_desc.get(p['display'], [])
        # exact date
        for n in negs:
            if n['date'] == p['date']:
                tax_value = n['proceeds']
                break
        # fallback ±1 day
        if not tax_value and p['date'] is not None:
            for n in negs:
                if n['date'] is None:
                    continue
                if abs((n['date'] - p['date']).days) <= 1:
                    tax_value = n['proceeds']
                    break
        date_out = p['date'].strftime("%d.%m.%Y") if p['date'] else ''
        print(f"{date_out}\t{p['display']}\t{p['proceeds']}\t{tax_value}")
    print('-' * terminal_width)


def get_interest_report(local_data):
    print('-' * terminal_width)
    data = copy.deepcopy(local_data)
    rows = data.get('Interest', [])

    def parse_date(row):
        try:
            return datetime.strptime(row['Date'], "%Y-%m-%d")
        except Exception:
            return datetime.min

    rows_sorted = sorted(rows, key=lambda r: (r['Currency'], parse_date(r)))

    # Build display rows: strip redundant leading "EUR " / "USD " from description
    display_rows = []
    for row in rows_sorted:
        try:
            dt = datetime.strptime(row['Date'], "%Y-%m-%d")
            date_out = dt.strftime("%d.%m.%Y")
        except Exception:
            date_out = row['Date']
        currency = row['Currency']
        desc = re.sub(r'^' + re.escape(currency) + r'\s+', '', row['Description'])
        display_rows.append((row['Amount'], currency, desc, date_out))

    # Column widths for console alignment (also tab-separated for Google Sheets paste)
    col_headers = ['Interest', 'Currency', 'Description', 'Date/Time']
    col_widths = [
        max(len(col_headers[0]), max((len(r[0]) for r in display_rows), default=0)),
        max(len(col_headers[1]), max((len(r[1]) for r in display_rows), default=0)),
        max(len(col_headers[2]), max((len(r[2]) for r in display_rows), default=0)),
        max(len(col_headers[3]), max((len(r[3]) for r in display_rows), default=0)),
    ]

    def fmt_row(cols):
        return '\t'.join(str(c).ljust(col_widths[i]) for i, c in enumerate(cols))

    print(fmt_row(col_headers))
    for r in display_rows:
        print(fmt_row(r))
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
                        help='List all dividend and dividend tax information.')
    parser.add_argument('-o', '--open-positions-report', action='store_true',
                        help='List all open positions information.')
    parser.add_argument('-f', '--forex-report', action='store_true', help='List all forex information.')
    parser.add_argument('-fd', '--forex-dividend-report', action='store_true',
                        help='List forex dividend payouts (Date, ISIN, IN_EUR).')
    parser.add_argument('-fdx', '--forex-dividend-tax-report', action='store_true',
                        help='List forex dividend payouts with tax (Date, ISIN, IN_EUR, Tax_Amount_in_EUR).')
    parser.add_argument('-i', '--interest-report', action='store_true',
                        help='List all interest payments (Interest, Currency, Description, Date/Time).')

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
