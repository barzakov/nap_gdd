import csv
import re
from pprint import pprint
from decimal import Decimal


class Parsestatementdatacsv:
    def __init__(self, filename):
        self.filename = filename

    @property
    def read_csv(self):
        data = {}
        with open(self.filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            # Commission Details'
            for row in reader:
                # Get Trade column names
                if ('Trades' == row['\ufeffStatement']) and \
                        row['Header'] == "Header" and \
                        row['Field Name'] == 'DataDiscriminator' and \
                        row['Field Value'] == 'Asset Category':
                    info_array_trade = row[None]
                # get all trades
                if row['\ufeffStatement'] == 'Trades' and \
                        row['Header'] == "Data" and \
                        row['Field Name'] == 'Order' and \
                        row['Field Value'] == 'Stocks':
                    if None in row:
                        my_trade_data = row[None]
                    else:
                        my_trade_data = []
                    my_current_name = row['Field Name']
                    my_trade_data.append(row['Field Value'])
                    my_trade_data[7] = str(abs(Decimal(my_trade_data[7])))
                    tiker = row[None][1]
                    if my_current_name not in data:
                        data[my_current_name] = {}
                    if tiker not in data[my_current_name]:
                        data[my_current_name][tiker] = []
                    trade_info_and_values = dict(zip(info_array_trade, my_trade_data))
                    data[my_current_name][tiker].append(trade_info_and_values)
                # Get dividend tax column names
                if row['\ufeffStatement'] == 'Withholding Tax' and \
                        row['Header'] == "Header" and \
                        row['Field Name'] == 'Currency' and \
                        row['Field Value'] == 'Date':
                    if None in row:
                        info_array_tax = row[None]
                    else:
                        info_array_tax = []
                # Get all dividend tax
                if row['\ufeffStatement'] == 'Withholding Tax' and \
                        row['Header'] == "Data" and \
                        'Withholding' not in row[None][0] and \
                        "Total" not in row['Field Name']:
                    if None in row:
                        my_tax_data = row[None]
                    else:
                        my_tax_data = []
                    my_tax_data.append(row['Field Value'])
                    my_tax_data[1] = str(abs(Decimal(my_tax_data[1])))
                    #pattern = r'(^[a-zA-Z0-9]+)(\([a-zA-Z0-9]+\)).* Cash Dividend (\w+) \d'
                    pattern = r'(^[a-zA-Z0-9]+)(\([a-zA-Z0-9]+\)).* (Cash Dividend|Payment in Lieu of Dividend).*'
                    is_in_currency = re.findall(pattern, my_tax_data[0])
                    is_in_currency = [tupal + (row['Field Name'],) for tupal in is_in_currency]
                    my_tax_data.append(is_in_currency[0][2])
                    my_tax_data.append(is_in_currency[0][0] + is_in_currency[0][1])
                    my_tax_data.append(is_in_currency[0][0])
                    if row['\ufeffStatement'] not in data:
                        data[row['\ufeffStatement']] = {}
                    if is_in_currency[0][0] not in data[row['\ufeffStatement']]:
                        data[row['\ufeffStatement']][is_in_currency[0][0]] = []
                    if info_array_tax:
                        if len(info_array_tax) < 4:
                            info_array_tax.append('Date')
                            info_array_tax.append('Currency')
                            info_array_tax.append('ISIN')
                            info_array_tax.append('Tiker')
                    tax_info_and_values = dict(zip(info_array_tax, my_tax_data))
                    data[row['\ufeffStatement']][is_in_currency[0][0]].append(tax_info_and_values)

                # Get Total dividend tax
                if row['\ufeffStatement'] == 'Withholding Tax' and \
                        row['Header'] == "Data" and \
                        "Total" == row['Field Name']:
                    my_all_tax_data = row[None]
                    data[row['\ufeffStatement'] + ' ' + row['Field Name']] = str(abs(Decimal(my_all_tax_data[1])))

                if row['\ufeffStatement'] == 'Withholding Tax' and \
                        row['Header'] == "Data" and \
                        "Total in EUR" == row['Field Name']:
                    my_all_tax_data = row[None]
                    data[row['\ufeffStatement'] + ' ' + row['Field Name']] = str(abs(Decimal(my_all_tax_data[1])))

                # Get dividend column names
                if row['\ufeffStatement'] == 'Dividends' and \
                        row['Header'] == "Header" and \
                        len(row[None]) == 3:
                    if None in row:
                        info_array_dividend = row[None]
                    else:
                        info_array_dividend = []
                # Get dividend data
                if row['\ufeffStatement'] == 'Dividends' and \
                        row['Header'] == "Data" and \
                        "Total" not in row['Field Name'] and \
                        len(row[None]) == 3:
                    if None in row:
                        my_dividend_data = row[None]
                    else:
                        my_dividend_data = []
                    my_dividend_data.append(row['Field Value'])
                    my_dividend_data[1] = str(abs(Decimal(my_dividend_data[1])))
                    pattern = r'(^[a-zA-Z0-9]+)(\([a-zA-Z0-9]+\)).* Cash Dividend (\w+) \d'
                    is_in_currency = re.findall(pattern, my_dividend_data[0])
                    my_dividend_data.append(is_in_currency[0][2])
                    my_dividend_data.append(is_in_currency[0][0] + is_in_currency[0][1])
                    my_dividend_data.append(is_in_currency[0][0])
                    if row['\ufeffStatement'] not in data:
                        data[row['\ufeffStatement']] = {}
                    if is_in_currency[0][0] not in data[row['\ufeffStatement']]:
                        data[row['\ufeffStatement']][is_in_currency[0][0]] = []
                    if info_array_dividend:
                        if len(info_array_dividend) < 4:
                            info_array_dividend.append('Date')
                            info_array_dividend.append('Currency')
                            info_array_dividend.append('ISIN')
                            info_array_dividend.append('Tiker')
                    dividend_info_and_values = dict(zip(info_array_dividend, my_dividend_data))
                    data[row['\ufeffStatement']][is_in_currency[0][0]].append(dividend_info_and_values)
                # Get Total dividend in USD
                if row['\ufeffStatement'] == 'Dividends' and \
                        row['Header'] == "Data" and \
                        "Total" == row['Field Name']:
                    my_all_payed_data = row[None]
                    data[row['\ufeffStatement'] + ' ' + row['Field Name'] + ' ' + 'USD'] = \
                        str(abs(Decimal(my_all_payed_data[1])))
                # Get Total dividend in EUR
                if row['\ufeffStatement'] == 'Dividends' and \
                        row['Header'] == "Data" and \
                        "Total in EUR" == row['Field Name']:
                    my_all_payed_data = row[None]
                    data[row['\ufeffStatement'] + ' ' + row['Field Name']] = \
                        str(abs(Decimal(my_all_payed_data[1])))
                # Cash Report row info
                if row['\ufeffStatement'] == 'Cash Report' and \
                        row['Header'] == "Header":
                    if None in row:
                        info_array_cash = row[None]
                    else:
                        info_array_cash = []
                    info_array_cash.append(row['Field Value'])
                    info_array_cash.append(row['Field Name'])
                # Cash Report row info
                if row['\ufeffStatement'] == 'Cash Report' and \
                        "Total" not in row['Field Name'] and \
                        row['Header'] == "Data":
                    if None in row:
                        my_cash_data = row[None]
                    else:
                        my_cash_data = []
                    my_cash_data.append(row['Field Value'])
                    my_cash_data.append(row['Field Name'])
                    if row['\ufeffStatement'] not in data:
                        data[row['\ufeffStatement']] = {}
                    if row['Field Name'] not in data[row['\ufeffStatement']]:
                        data[row['\ufeffStatement']][row['Field Name']] = []
                    cash_info_and_values = dict(zip(info_array_cash, my_cash_data))
                    data[row['\ufeffStatement']][row['Field Name']].append(cash_info_and_values)
                # Net Asset row info
                if row['\ufeffStatement'] == 'Net Asset Value' and \
                        row['Header'] == "Header":
                    if None in row:
                        info_array_net = row[None]
                    else:
                        info_array_net = []
                    info_array_net.append(row['Field Value'])
                    info_array_net.append(row['Field Name'])
                # Net Asset value
                if row['\ufeffStatement'] == 'Net Asset Value' and \
                        row['Header'] == "Data":
                    if None in row:
                        my_net_data = row[None]
                    else:
                        my_net_data = []
                    my_net_data.append(row['Field Value'])
                    my_net_data.append(row['Field Name'])
                    if row['\ufeffStatement'] not in data:
                        data[row['\ufeffStatement']] = {}
                    if row['Field Name'] not in data[row['\ufeffStatement']]:
                        data[row['\ufeffStatement']][row['Field Name']] = []
                    net_info_and_values = dict(zip(info_array_net, my_net_data))
                    data[row['\ufeffStatement']][row['Field Name']].append(net_info_and_values)
                # Open Positions row info
                if row['\ufeffStatement'] == 'Open Positions' and \
                        row['Header'] == "Header":
                    if None in row:
                        info_array_open = row[None]
                    else:
                        info_array_open = []
                    info_array_open.append(row['Field Value'])
                    info_array_open.append(row['Field Name'])
                # Open Positions Report row info
                if row['\ufeffStatement'] == 'Open Positions' and \
                        row['Header'] == "Data":
                    if None in row:
                        my_open_data = row[None]
                    else:
                        my_open_data = []
                    my_open_data.append(row['Field Value'])
                    my_open_data.append(row['Field Name'])
                    if row['\ufeffStatement'] not in data:
                        data[row['\ufeffStatement']] = {}
                    if row['Field Name'] not in data[row['\ufeffStatement']]:
                        data[row['\ufeffStatement']][row['Field Name']] = []
                    open_info_and_values = dict(zip(info_array_open, my_open_data))
                    data[row['\ufeffStatement']][row['Field Name']].append(open_info_and_values)
                # forex: Header / Data / Total (same style as other sections)
                if row['\ufeffStatement'] == 'Forex P/L Details' and row['Header'] == 'Header':
                    if None in row:
                        info_array_forex = row[None]
                    else:
                        info_array_forex = []

                if row['\ufeffStatement'] == 'Forex P/L Details' and row['Header'] == 'Data' and "Total" not in row['Field Name']:
                    if None in row:
                        my_forex_data = row[None]
                    else:
                        my_forex_data = []
                    # keep the same approach: append Field Value as other sections do
                    my_forex_data.append(row['Field Value'])
                    # build dict from header -> values
                    if info_array_forex:
                        forex_info_and_values = dict(zip(info_array_forex, my_forex_data))
                    else:
                        # fallback: create keys col_0..col_n
                        keys = [f"col_{i}" for i in range(len(my_forex_data))]
                        forex_info_and_values = dict(zip(keys, my_forex_data))
                    # choose grouping key similar to other sections
                    group_key = forex_info_and_values.get('Description') or forex_info_and_values.get('Asset Category') or 'Unknown'
                    if 'Forex' not in data:
                        data['Forex'] = {}
                    if group_key not in data['Forex']:
                        data['Forex'][group_key] = []
                    data['Forex'][group_key].append(forex_info_and_values)

                if row['\ufeffStatement'] == 'Forex P/L Details' and row['Header'] == 'Data' and "Total" == row['Field Name']:
                    my_all_forex_data = row[None] if None in row else []
                    # keep totals as a list of non-empty values (mirrors safe handling used elsewhere)
                    totals = [v.strip() for v in my_all_forex_data if v and v.strip() != ""]
                    data['Forex Total'] = totals

                # Financial Instrument Information data
                if row['\ufeffStatement'] == 'Financial Instrument Information' and row['Header'] == 'Header':
                    if None in row:
                        info_array_instrument = row[None]
                        info_array_instrument.append(row['Field Value'])
                        info_array_instrument.append(row['Field Name'])
                    else:
                        info_array_instrument = []
                if row['\ufeffStatement'] == 'Financial Instrument Information' and row['Header'] == 'Data':
                    # collect data values from the row starting from the third field
                    fieldnames = list(row.keys())
                    if None in row:
                        my_instrument_data = row[None]
                        my_instrument_data.append(row['Field Value'])
                        my_instrument_data.append(row['Field Name'])
                    else:
                        my_instrument_data = []

                    # build mapping header -> value
                    instrument_info = dict(zip(info_array_instrument, my_instrument_data))
                    # replace empty values with UNSET_<ColumnName>
                    for hk in instrument_info:
                        v = instrument_info.get(hk)
                        if v is None or (isinstance(v, str) and v.strip() == ""):
                            instrument_info[hk] = f"UNSET_{hk.replace(' ', '_')}"
                        else:
                            instrument_info[hk] = str(v).strip()
                    period = data['Statement']['Period']
                    end_year_match = re.search(r'(\d{4})(?!\d)', period)
                    end_year = int(end_year_match.group(1)) if end_year_match else None
                    if end_year <= 2024:
                        instrument_information_tiker_to_use = 'Symbol'
                    else:
                        instrument_information_tiker_to_use = 'Underlying'
                    # determine symbol key (first token before comma) or UNSET_Symbol
                    raw_underlaying_symbol = instrument_info.get(instrument_information_tiker_to_use) or ""
                    if raw_underlaying_symbol and not raw_underlaying_symbol.startswith('UNSET_'):
                        underlaying_symbol_key = raw_underlaying_symbol
                    else:
                        underlaying_symbol_key = "UNSET_Symbol"
                    # store the instrument_info under top-level Instrument Information keyed by underlaying_symbol_key
                    if 'Instrument Information' not in data:
                        data['Instrument Information'] = {}
                    data['Instrument Information'][underlaying_symbol_key] = instrument_info

                # Interest data
                if row['\ufeffStatement'] == 'Interest' and \
                        row['Header'] == 'Data' and \
                        row['Field Name'] not in ('Total', 'Total in EUR', 'Total Interest in EUR'):
                    currency = row['Field Name']
                    date = row['Field Value']
                    extras = row[None] if None in row else []
                    description = extras[0] if len(extras) > 0 else ''
                    amount = extras[1] if len(extras) > 1 else ''
                    if 'Interest' not in data:
                        data['Interest'] = []
                    data['Interest'].append({
                        'Currency': currency,
                        'Date': date,
                        'Description': description,
                        'Amount': amount,
                    })

                # Statement row Period info
                if row['\ufeffStatement'] == 'Statement' and row['Field Name'] == "Period":
                    data['Statement'] = {"Period":row['Field Value']}

            return data
