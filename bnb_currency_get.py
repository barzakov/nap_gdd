#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import argparse

def fetch_data(start_date, end_date, currency):
    base_url = (
        "https://www.bnb.bg/Statistics/StExternalSector/StExchangeRates/StERForeignCurrencies/index.htm"
        "?downloadOper=&group1=second&periodStartDays={}&periodStartMonths={}&periodStartYear={}"
        "&periodEndDays={}&periodEndMonths={}&periodEndYear={}&valutes={}&search=true&showChart=false&showChartButton=true"
    )

    url = base_url.format(
        start_date.day, start_date.month, start_date.year,
        end_date.day, end_date.month, end_date.year,
        currency
    )

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Failed to fetch data for {start_date} to {end_date} with currency={currency}: {e}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')

    extracted_data = {}
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 4:  # Match rows with 4 cells
            try:
                date = cells[0].text.strip()
                rate = cells[2].text.strip()
                # Check if rate is valid (i.e., not empty)
                if rate:
                    date_obj = datetime.strptime(date, "%d.%m.%Y")
                    extracted_data[date_obj] = rate
            except (IndexError, AttributeError):
                continue

    return extracted_data

def generate_date_range(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)

def fill_missing_dates(all_data, start_date, end_date):
    if not all_data:
        return []

    sorted_dates = sorted(all_data.keys())
    filled_data = []
    
    previous_rate = None

    # Check for the last known rate before start_date if it exists
    for date in sorted_dates:
        if date < start_date:
            previous_rate = all_data[date]
        else:
            break

    for current_date in generate_date_range(start_date, end_date):
        if current_date in all_data:
            previous_rate = all_data[current_date]
            filled_data.append((current_date.strftime("%d.%m.%Y"), previous_rate))
        else:
            # Use the last known rate for the missing date
            if previous_rate:
                filled_data.append((current_date.strftime("%d.%m.%Y"), previous_rate))
            else:
                filled_data.append((current_date.strftime("%d.%m.%Y"), None))  # If no previous, None

    return filled_data

def main():
    parser = argparse.ArgumentParser(description="Fetch currency exchange rates")
    parser.add_argument("--year", type=int, required=True, help="Year for data")
    parser.add_argument("--currency", required=True, help="Currency (e.g., USD, EUR)")

    args = parser.parse_args()
    
    start_year = args.year
    start_month = 1
    months_interval = 3

    start_date = datetime(start_year, start_month, 1)
    results = []

    all_currency_data = {}

    currency = args.currency

    while start_date.year == start_year:
        # Calculate the end_date for each interval (3 months period)
        end_date = start_date + timedelta(days=89)
        end_date = datetime(end_date.year, end_date.month, 1) - timedelta(days=1)

        if end_date.year > start_year or (end_date.year == start_year and end_date.month > 12):
            end_date = datetime(start_year, 12, 31)

        html_content = fetch_data(start_date, end_date, currency)
        if html_content:
            data = html_content
            if data:
                # Store fetched data into a dictionary by dates
                all_currency_data.update(data)

        start_date = end_date + timedelta(days=1)

    # Now fill missing dates using previously fetched data
    filled_data = fill_missing_dates(all_currency_data, datetime(start_year, start_month, 1), end_date)

    for row in filled_data:
        print(f"{row[0]} {row[1] if row[1] else 'None'}")

if __name__ == "__main__":
    main()

