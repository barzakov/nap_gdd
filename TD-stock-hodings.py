#!/usr/bin/env python3
import argparse
import shutil
import os
import csv
from decimal import Decimal
from datetime import datetime
from Trades.utils import Parsestatementdatacsv

# try tomllib (py3.11+), fallback to toml package
try:
    import tomllib as toml
except Exception:
    import toml

terminal_width = shutil.get_terminal_size().columns


def _to_decimal(value):
    # normalize quantity/price string, handle commas and possible leading +/-
    return Decimal(value.replace(",", ""))


def _load_ticker_map():
    # load mapping from TD-stock-hodings.toml next to this script
    cfg_path = os.path.join(os.path.dirname(__file__), "TD-stock-hodings.toml")
    if not os.path.exists(cfg_path):
        return {}, {}
    try:
        with open(cfg_path, "rb") as f:
            cfg = toml.load(f)
            yahoo = cfg.get("ticker_ibkr_to_yahoo", {})
            underlying = cfg.get("ticker_ibkr_to_uderlaying_ticker", {})
            return yahoo, underlying
    except Exception:
        return {}, {}


def _parse_open_positions_csv(filename):
    """Parse Open Positions section from CSV file."""
    positions = []
    try:
        with open(filename, 'r', newline='') as csvfile:
            # Read all lines and find the Open Positions section
            lines = csvfile.readlines()
            op_header_idx = None
            # Find the header row for Open Positions
            for i, line in enumerate(lines):
                if line.startswith('Open Positions,Header,'):
                    op_header_idx = i
                    break
            
            if op_header_idx is None:
                return positions
            
            # Parse header
            header_line = lines[op_header_idx].strip()
            header_fields = header_line.split(',')
            
            # Parse data rows starting from next line
            for i in range(op_header_idx + 1, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                # Only process Open Positions lines
                if not line.startswith('Open Positions,'):
                    # Stop if we encounter a different statement type
                    if not line.startswith('Open Positions'):
                        break
                    continue
                
                # Skip total rows
                if ',Total,' in line:
                    continue
                
                # Only process Data rows
                if not line.startswith('Open Positions,Data,'):
                    continue
                
                fields = line.split(',')
                if len(fields) < len(header_fields):
                    # Pad with empty strings if needed
                    fields.extend([''] * (len(header_fields) - len(fields)))
                
                row_dict = dict(zip(header_fields, fields[:len(header_fields)]))
                
                symbol = row_dict.get('Symbol', '').strip()
                currency = row_dict.get('Currency', '').strip()
                quantity = row_dict.get('Quantity', '').strip()
                cost_price = row_dict.get('Cost Price', '').strip()
                data_disc = row_dict.get('DataDiscriminator', '').strip()
                
                # skip rows without symbol
                if not symbol:
                    continue
                
                positions.append({
                    'Symbol': symbol,
                    'Currency': currency,
                    'Quantity': quantity,
                    'Cost Price': cost_price,
                    'DataDiscriminator': data_disc
                })
    except Exception as e:
        pass
    return positions


def _apply_underlying_symbol(symbol, underlying_map):
    # map IBKR instrument ticker to underlying ticker when present
    if not underlying_map:
        return symbol
    return underlying_map.get(symbol, symbol)


def _symbol_with_suffix(symbol, yahoo_map, add_suffix):
    if not add_suffix or not yahoo_map:
        return symbol
    for suffix, tickers in yahoo_map.items():
        if symbol in tickers:
            return f"{symbol}{suffix}"
    return symbol


def print_buy_report(data, yahoo_map=None, underlying_map=None, add_suffix=True):
    # print buy trades (Quantity > 0)
    if 'Order' not in data:
        print("No trade data found.")
        return
    rows = []
    for ticker in data['Order']:
        for order in data['Order'][ticker]:
            try:
                q = _to_decimal(order['Quantity'])
            except Exception:
                continue
            if q > 0:
                # parse date for sorting: use date-only part (YYYY-MM-DD) to match get_statement_data.py
                try:
                    date_part = order['Date/Time'].split(',')[0]
                except Exception:
                    date_part = ""
                # ensure symbol and price are defined
                symbol = order.get('Symbol', ticker)
                price = order.get('T. Price', '')
                # apply underlying mapping first, then suffix mapping
                mapped_symbol = _apply_underlying_symbol(symbol, underlying_map)
                symbol_key = _symbol_with_suffix(mapped_symbol, yahoo_map, add_suffix)
                # store date_part as string key (same logic as get_statement_data.py)
                rows.append((date_part, symbol_key, order['Quantity'], price))
    if rows:
        # sort by date string (YYYY-MM-DD) to match get_statement_data.py
        rows.sort(key=lambda x: x[0])
        print('-' * terminal_width)
        print("Symbol\tShares\tPurchase")
        for _, sym, qty, pr in rows:
            print(f"{sym}\t{qty}\t{pr}")
        print('-' * terminal_width)  # closing separator (added)
    else:
        print("No buy trades found.")


def print_sell_report(data, yahoo_map=None, underlying_map=None, add_suffix=True):
    # print sell trades (Quantity < 0)
    if 'Order' not in data:
        print("No trade data found.")
        return
    rows = []
    for ticker in data['Order']:
        for order in data['Order'][ticker]:
            try:
                q = _to_decimal(order['Quantity'])
            except Exception:
                continue
            if q < 0:
                # parse date for sorting: use date-only part (YYYY-MM-DD) to match get_statement_data.py
                try:
                    date_part = order['Date/Time'].split(',')[0]
                except Exception:
                    date_part = ""
                # ensure symbol, price, shares are defined
                symbol = order.get('Symbol', ticker)
                price = order.get('T. Price', '')
                shares = str(abs(q))
                # apply underlying mapping first, then suffix mapping
                mapped_symbol = _apply_underlying_symbol(symbol, underlying_map)
                symbol_key = _symbol_with_suffix(mapped_symbol, yahoo_map, add_suffix)
                rows.append((date_part, symbol_key, shares, 'Not_Added', price))
    if rows:
        # sort by date string (YYYY-MM-DD) to match get_statement_data.py
        rows.sort(key=lambda x: x[0])
        print('-' * terminal_width)
        print("Symbol\tShares\tPurchase Price\tSell Price")
        for _, sym, sh, purchase, sell in rows:
            print(f"{sym}\t{sh}\t{purchase}\t{sell}")
        print('-' * terminal_width)  # closing separator (added)
    else:
        print("No sell trades found.")


def print_open_positions(filename, currency=None, yahoo_map=None, underlying_map=None, add_suffix=True):
    # print open positions filtered by currency (EUR or USD)
    positions = _parse_open_positions_csv(filename)
    rows = []
    
    for entry in positions:
        # check currency filter
        entry_currency = entry.get('Currency', '').upper()
        if currency and entry_currency != currency.upper():
            continue
        symbol = entry.get('Symbol', '').strip()
        if not symbol:
            continue
        try:
            quantity = _to_decimal(entry.get('Quantity', '0'))
        except Exception:
            continue
        
        cost_price = entry.get('Cost Price', '').strip()
        
        # apply underlying mapping first, then suffix mapping
        mapped_symbol = _apply_underlying_symbol(symbol, underlying_map)
        symbol_key = _symbol_with_suffix(mapped_symbol, yahoo_map, add_suffix)
        rows.append((symbol_key, str(quantity), cost_price))
    
    if rows:
        print('-' * terminal_width)
        print("Symbol\tQuantity\tCost Price")
        for sym, qty, price in rows:
            print(f"{sym}\t{qty}\t{price}")
        print('-' * terminal_width)
    else:
        currency_filter = f" ({currency})" if currency else ""
        print(f"No open positions found{currency_filter}.")


def main():
    # keep formatting in help text for readability
    parser = argparse.ArgumentParser(
        description='TD stock holdings - file_name must be a CSV (required). Use -b/--buy or -s/--sell or -oe/-ou for open positions.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Default behavior: adds exchange suffix using TD-stock-hodings.toml.\n"
            "Use -d/--debug to disable and keep original tickers.\n\n"
            "IBKR Code            Yahoo Suffix    Exchange\n"
            "-------------------  -------------   -------------------------------\n"
            "IBIS / IBIS2 /BM     .DE             Xetra (Germany)\n"
            "FWB / FWB2           .F              Frankfurt Stock Exchange (Germany)\n"
            "SBF                  .PA             Euronext Paris (France)\n"
            "AEB                  .AS             Euronext Amsterdam (Netherlands)\n"
            "BVME                 .MI             Borsa Italiana — Milan (Italy)\n"
        )
    )
    parser.add_argument('file_name', help='Statement csv file (must be .csv)')
    parser.add_argument('-b', '--buy', action='store_true', help='List buy trades only (positive Quantity)')
    parser.add_argument('-s', '--sell', action='store_true', help='List sell trades only (negative Quantity)')
    parser.add_argument('-oe', '--open-eur', action='store_true', help='List open positions in EUR currency')
    parser.add_argument('-ou', '--open-usd', action='store_true', help='List open positions in USD currency')
    parser.add_argument('-d', '--debug', action='store_true', help='Disable exchange suffix mapping (old behavior)')
    args = parser.parse_args()

    if not args.file_name.lower().endswith('.csv'):
        print("Error: file_name must be a .csv")
        return

    # load ticker mappings (yahoo suffix map, underlying ticker map)
    yahoo_map, underlying_map = _load_ticker_map()

    add_suffix = not args.debug

    # For -oe and -ou, we don't need the Parsestatementdatacsv reader
    if args.open_eur:
        print_open_positions(args.file_name, currency='EUR', yahoo_map=yahoo_map, underlying_map=underlying_map, add_suffix=add_suffix)
        return
    if args.open_usd:
        print_open_positions(args.file_name, currency='USD', yahoo_map=yahoo_map, underlying_map=underlying_map, add_suffix=add_suffix)
        return

    # For other options, use the standard reader
    reader = Parsestatementdatacsv(args.file_name)
    data = reader.read_csv

    if args.buy:
        print_buy_report(data, yahoo_map, underlying_map, add_suffix)
    if args.sell:
        print_sell_report(data, yahoo_map, underlying_map, add_suffix)
    if not (args.buy or args.sell or args.open_eur or args.open_usd):
        parser.print_help()

if __name__ == "__main__":
    main()