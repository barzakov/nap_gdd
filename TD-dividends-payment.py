#!/usr/bin/env python3
import argparse
import os
from datetime import datetime
from Trades.utils import Parsestatementdatacsv
import re

# try tomllib (py3.11+), fallback to toml package
try:
    import tomllib as toml
except Exception:
    import toml


def _load_ticker_map():
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


def _apply_underlying_symbol(symbol, underlying_map):
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


def _extract_base_ticker(desc):
    # expect patterns like "MSF(US5949181045) ..." -> extract MSF
    if not desc:
        return ""
    m = __import__('re').match(r'^([A-Za-z0-9\-]+)\(', desc.strip())
    return m.group(1) if m else desc.split()[0]


def _is_cash_dividend(desc: str) -> bool:
    if not desc:
        return False
    # accept truncated endings like "Cash Dividen..", "Cash D.." etc.
    return bool(re.search(r'cash\s+div\w{0,6}\.*\s*$', desc, re.IGNORECASE))


def run():
    parser = argparse.ArgumentParser(description="Report forex dividends (EUR) from statement csv")
    parser.add_argument("file_name", help="Statement csv file with all possible information")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Disable exchange suffix mapping (keep original tickers)")
    args = parser.parse_args()

    yahoo_map, underlying_map = _load_ticker_map()
    add_suffix = not args.debug

    reader = Parsestatementdatacsv(args.file_name)
    data = reader.read_csv

    rows = []
    # iterate through Forex entries
    for group_key in data.get('Forex', {}):
        for entry in data['Forex'][group_key]:
            desc = entry.get('Description', '') or ''
            # only cash dividends (allow truncated endings)
            if not _is_cash_dividend(desc):
                continue
            qty = str(entry.get('Quantity', '')).strip()
            # only payouts (quantity not starting with '-')
            if qty.startswith('-'):
                continue
            date_raw = entry.get('Date/Time', entry.get('Date', ''))
            # parse date
            dt = None
            try:
                dt = datetime.strptime(date_raw, "%Y-%m-%d, %H:%M:%S")
            except Exception:
                try:
                    dt = datetime.strptime(date_raw, "%Y-%m-%d")
                except Exception:
                    dt = None
            if not dt:
                continue
            base = _extract_base_ticker(desc)
            mapped = _apply_underlying_symbol(base, underlying_map)
            symbol_key = _symbol_with_suffix(mapped, yahoo_map, add_suffix)
            proceeds = entry.get('Proceeds in EUR', '')
            # Month format: e.g. "December '22" (wrap month label in quotes)
            month_label = f"\"{dt.strftime('%B')} '{dt.strftime('%y')}'\""
            # Date format: M/D/YY without leading zeros
            date_label = f"{dt.month}/{dt.day}/{dt.year % 100}"
            rows.append((dt, month_label, symbol_key, proceeds, date_label))

    # sort by date ascending
    rows.sort(key=lambda r: r[0] or datetime.max)

    # print
    print("Month\tSymbol\tDividends\tDate")
    for _dt, month_label, symbol_key, proceeds, date_label in rows:
        print(f"{month_label}\t{symbol_key}\t{proceeds}\t{date_label}")


if __name__ == "__main__":
    run()