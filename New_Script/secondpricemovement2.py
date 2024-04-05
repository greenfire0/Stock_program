import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import pandas as pd
import requests
from datetime import datetime, timedelta
from urllib.request import urlopen
import webbrowser
import requests
import bs4

root = tk.Tk()
window_location = "1000x600"
root.geometry(window_location)
root.configure(bg='black')
root.option_add('*Font', 'Times 12')

# Padding for all widgets
padx = 5

# Ticker Label
ticker_label = tk.Label(root, text="Ticker:", bg='black', fg='white')
ticker_label.grid(row=0, column=0, sticky='w', padx=padx, pady=5)

# Ticker Entry
ticker_entry = tk.Entry(root, width=6, bg='white', fg='black')
ticker_entry.grid(row=0, column=1, sticky='w', padx=padx, pady=5)
ticker_entry.focus_set()  # Set focus to the ticker entry

# Dates Label
dates_label = tk.Label(root, text="Dates:", bg='black', fg='white')
dates_label.grid(row=1, column=0, sticky='w', padx=padx)

# Start Date Entry
start_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
start_date_entry.grid(row=1, column=1, sticky='w', padx=padx)
start_date_entry.set_date(datetime.now() - timedelta(days=729))  # Set default start date to 729 days ago

# End Date Entry
end_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
end_date_entry.grid(row=1, column=2, sticky='w', padx=padx)
end_date_entry.set_date(datetime.now() - timedelta(days=1))  # Set default end date to yesterday

# Market Session Label
session_label = tk.Label(root, text="Session:", bg='black', fg='white')
session_label.grid(row=2, column=0, sticky='w', padx=padx)

# Market Session Dropdown
session_var = tk.StringVar()
session_dropdown = ttk.Combobox(root, textvariable=session_var, values=['All', 'Premarket', 'Market', 'Aftermarket'], width=12)
session_dropdown.grid(row=2, column=1, sticky='w', padx=padx)
session_dropdown.current(0)  # Set 'All' as the default selection
session_dropdown.bind('<Button-1>', lambda event: event.widget.event_generate('<Down>'))  # Open dropdown when clicked anywhere within it

# Earnings Label
earnings_label = tk.Label(root, text="Earnings:", bg='black', fg='white')
earnings_label.grid(row=3, column=0, sticky='w', padx=padx)

# Earnings Dropdown
earnings_var = tk.StringVar()
earnings_dropdown = ttk.Combobox(root, textvariable=earnings_var, values=['Earnings', 'Normal'], width=12)
earnings_dropdown.grid(row=3, column=1, sticky='w', padx=padx)
earnings_dropdown.current(0)  # Set 'Earnings' as the default selection
earnings_dropdown.bind('<Button-1>', lambda event: event.widget.event_generate('<Down>'))  # Open dropdown when clicked anywhere within it

# Result Text
result_text = tk.Text(root, bg='black', fg='white')
result_text.grid(row=4, column=0, columnspan=3, sticky='ew', padx=padx,pady=5)  # Make the result text widget stretch to fill the available space
root.grid_columnconfigure(0, weight=1)  # Make the column containing the result text widget expand

# News Text
news_text = tk.Text(root, bg='black', fg='white')
news_text.grid(row=4, column=3, sticky='ew', padx=padx, pady=5)  # Make the news text widget stretch to fill the available space
root.grid_columnconfigure(3, weight=1)  # Make the column containing the news text widget expand

# earnings data
earnings_text = tk.Text(root, bg='black', fg='white', width=80, height=10)
earnings_text.grid(row=5, column=0, columnspan=3, sticky='w', padx=padx, pady=5)

def get_earnings_prices(ticker, date):
    # Placeholder function. Replace with actual implementation.
    return 100, 200

def get_earnings_data(ticker):
    two_years_ago = datetime.now() - timedelta(days=730)  # Calculate date two years ago
    url = f"https://www.alphaquery.com/stock/{ticker}/earnings-history"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                earnings_data = []
                for row in rows:
                    columns = row.find_all('td')
                    date = columns[0].text.strip()
                    # Format the date to match yfinance's expected format
                    formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
                    if datetime.strptime(formatted_date, '%Y-%m-%d') >= two_years_ago:  # Check if the date is within the past two years
                        estimated_eps = columns[2].text.strip()
                        actual_eps = columns[3].text.strip()

                        # Fetch historical prices for the earnings date
                        earnings_low, earnings_high = get_earnings_prices(ticker, formatted_date)

                        earnings_data.append((formatted_date, earnings_low, earnings_high, estimated_eps, actual_eps))
                return earnings_data
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error fetching earnings data: {e}")
        return None


def open_link(event):
    start = news_text.index("@%s,%s" % (event.x, event.y))
    end = news_text.index("%s lineend" % start)
    url = news_text.get(start, end)
    webbrowser.open(url)

news_text.tag_configure("hyperlink", foreground="deep sky blue", underline=1)
news_text.tag_bind("hyperlink", "<Button-1>", open_link)


def fetch_data_based_on_option():
    # Get the selected option
    selected_option = earnings_var.get()

    # Get the ticker
    ticker = ticker_entry.get().strip().upper()

    # Get the start and end dates
    start_date = start_date_entry.get_date().strftime('%Y-%m-%d')
    end_date = end_date_entry.get_date().strftime('%Y-%m-%d')

    # Get selected market session
    session = session_var.get()

    # Define your API key
    api_key = "4Jq5Ew8tmnwkv_Q8CMEvNGnwAqJp2AzX"

    # Define the parameters for the API request
    multiplier = "5"  # 5-minute bars
    timespan = "minute"  # Time span for the bars

    earnings_data = get_earnings_data(ticker)
    if earnings_data:
        filtered_dfs = []
        for earnings_date, next_day, *rest in earnings_data:
            # Construct start and end dates for filtering
            start_date = earnings_date
            end_date = next_day

    

    # Display earnings data
    earnings_text.delete(1.0, tk.END)
    if earnings_data:
        for data in earnings_data:
            earnings_date, next_day, low, high, estimated_eps, actual_eps, *rest = data
            earnings_text.insert(tk.END, f"Earnings data for {earnings_date}: Low - {low}, High - {high}, Estimated EPS - {estimated_eps}, Actual EPS - {actual_eps}\n")


def search_stock(event=None):
    result_text.delete(1.0, tk.END)  # Clear previous results
    news_text.delete(1.0, tk.END)  # Clear previous news
    earnings_text.delete(1.0, tk.END)  # Clear previous earnings data

    ticker = ticker_entry.get().strip().upper()  # Get the ticker and remove any leading/trailing whitespace
    if not ticker:  # If ticker is empty
        result_text.insert(tk.END, "Please enter a ticker symbol.")
        return

    # Get start and end dates
    start_date = start_date_entry.get_date().strftime('%Y-%m-%d')
    end_date = end_date_entry.get_date().strftime('%Y-%m-%d')

    # Get selected market session
    session = session_var.get()

    # Define your API key
    api_key = "4Jq5Ew8tmnwkv_Q8CMEvNGnwAqJp2AzX"

    # Define the parameters for the API request
    multiplier = "5"  # 5-minute bars
    timespan = "minute"  # Time span for the bars

    # Construct the API request URL
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}?apiKey={api_key}"

    # Send the GET request to the Polygon API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        json_data = response.json()
        # Check if 'results' key is in the JSON data
        if 'results' in json_data:
            # Convert the JSON data to a DataFrame
            df = pd.DataFrame(json_data['results'])
            df['timestamp'] = pd.to_datetime(df['t'], unit='ms') - pd.Timedelta(hours=5)

            df.set_index('timestamp', inplace=True)

            # Filter data based on selected market session
            if session == 'Premarket':
                df = df.between_time('04:00', '09:30')
            elif session == 'Market':
                df = df.between_time('09:30', '16:00')
            elif session == 'Aftermarket':
                df = df.between_time('16:00', '20:00')




    # Fetch news headlines
    url = f"https://api.polygon.io/v2/reference/news?ticker={ticker}&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        if 'results' in json_data:
            for article in json_data['results']:
                published_date = datetime.strptime(article['published_utc'], '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = published_date.strftime('%m/%d %H:%M')
                news_text.insert(tk.END, f"{formatted_date}: {article['title']}\n")
                news_text.insert(tk.END, f"{article['article_url']}\n\n", "hyperlink")
        else:
            news_text.insert(tk.END, "No 'results' in the returned data.")
    else:
        news_text.insert(tk.END, "Failed to fetch news from Polygon API")

    earnings_text.delete(1.0, tk.END)
    earnings_data = get_earnings_data(ticker)
    if earnings_data:
        for data in earnings_data:
            earnings_date,  low, high, estimated_eps, actual_eps, *rest = data
            earnings_text.insert(tk.END, f"Earnings data for {earnings_date}: Low - {low}, High - {high}, Estimated EPS - {estimated_eps}, Actual EPS - {actual_eps}\n")

def clear():
    result_text.delete(1.0, tk.END)
    news_text.delete(1.0, tk.END)
    ticker_entry.delete(0, tk.END)
    start_date_entry.set_date(datetime.now() - timedelta(days=729))
    end_date_entry.set_date(datetime.now() - timedelta(days=1))
    session_dropdown.current(0)
    earnings_text.delete(1.0, tk.END)
    


# Search Button
search_button = tk.Button(root, text="Search", bg='blue', fg='white', command=search_stock)
search_button.grid(row=0, column=2, sticky='w', padx=padx, pady=5)

# Clear Button
clear_button = tk.Button(root, text="Clear", bg='grey', fg='white', command=clear)
clear_button.grid(row=0, column=2, sticky='w', padx=65, pady=5)

# Bind Enter key to search_stock function
root.bind('<Return>', search_stock)

root.mainloop()