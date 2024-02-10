import csv
import re
# from pprint import pprint


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
                    my_trade_data[7] = str(abs(float(my_trade_data[7])))
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
                        "Total" not in row['Field Name']:
                    if None in row:
                        my_tax_data = row[None]
                    else:
                        my_tax_data = []
                    my_tax_data.append(row['Field Value'])
                    my_tax_data[1] = str(abs(float(my_tax_data[1])))
                    pattern = r'(^[a-zA-Z0-9]+)(\([a-zA-Z0-9]+\)).* Cash Dividend (\w+) \d'
                    is_in_currency = re.findall(pattern, my_tax_data[0])
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
                    data[row['\ufeffStatement'] + ' ' + row['Field Name']] = str(abs(float(my_all_tax_data[1])))

                if row['\ufeffStatement'] == 'Withholding Tax' and \
                        row['Header'] == "Data" and \
                        "Total in EUR" == row['Field Name']:
                    my_all_tax_data = row[None]
                    data[row['\ufeffStatement'] + ' ' + row['Field Name']] = str(abs(float(my_all_tax_data[1])))

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
                    my_dividend_data[1] = str(abs(float(my_dividend_data[1])))
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
                        str(abs(float(my_all_payed_data[1])))
                # Get Total dividend in EUR
                if row['\ufeffStatement'] == 'Dividends' and \
                        row['Header'] == "Data" and \
                        "Total in EUR" == row['Field Name']:
                    my_all_payed_data = row[None]
                    data[row['\ufeffStatement'] + ' ' + row['Field Name']] = \
                        str(abs(float(my_all_payed_data[1])))
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
        return data
