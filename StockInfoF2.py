
import requests
import bs4
import datetime
import PySimpleGUI as sg
import yfinance as yf
import re
from finvizfinance.quote import finvizfinance
import matplotlib.pyplot as plt


class StockInfoApp:
    def __init__(self):
        sg.theme('Black')

        # Define dark theme colors
        dark_theme_bg = 'black'
        dark_theme_fg = 'white'
        dark_theme_outline = '#505050'

        # Ticker Frame
        self.ticker_frame = sg.Column([
            [sg.Text('Ticker:', text_color='white'), 
             sg.Input(key='-TICKER-', text_color='black', size=(6, None), background_color='white', enable_events=True),
             sg.Button('Search', key='-SEARCH-', button_color=('white', 'green'))]
        ], background_color=dark_theme_bg)

        # Middle Left Frame
        self.middle_left_frame = sg.Column([[sg.Multiline(size=(60, 20), key='-INFO-', background_color=dark_theme_bg, text_color=dark_theme_fg, auto_refresh=True, disabled=True, no_scrollbar=True)]], background_color=dark_theme_bg)

        # Finviz Frame
        self.finviz_frame = sg.Column([[sg.Multiline(size=(30, 20), key='-FINVIZ-', background_color=dark_theme_bg, text_color=dark_theme_fg, auto_refresh=True, reroute_stdout=True, disabled=True, no_scrollbar=True)]], background_color=dark_theme_bg)

        # Placeholder Frame
        self.placeholder_frame = sg.Column([[sg.Multiline(size=(30, 20), key='-PLACEHOLDER-', background_color=dark_theme_bg, text_color=dark_theme_fg, auto_refresh=True, reroute_stdout=True, disabled=True, no_scrollbar=True)]], background_color=dark_theme_bg)

        # Earnings Frame
        self.earnings_frame = sg.Column([[sg.Multiline(size=(60, 10), key='-EARNINGS-', background_color=dark_theme_bg, text_color=dark_theme_fg, auto_refresh=True, reroute_stdout=True, disabled=True, no_scrollbar=True)]], background_color=dark_theme_bg)

        self.layout = [
            [sg.Text('Stock Information', font=('Helvetica', 16), text_color='white', background_color=dark_theme_bg)],
            [self.ticker_frame],
            [sg.Column([[self.middle_left_frame, self.finviz_frame, self.placeholder_frame]], element_justification='stretch')],
            [self.earnings_frame]
       ]

        window_location = (0, 0)
        self.window = sg.Window('Stock Information', self.layout, grab_anywhere=True, finalize=True, location=window_location)

        # Hotkey to focus on the ticker input box
        self.window.bind('<Control-Shift-d>', '+Ctrl+Shift+d')

    def run(self):
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == '-SEARCH-':
                ticker = values['-TICKER-'].upper()
                self.show_stock_info(ticker)

        self.window.close()



    def show_stock_info(self, ticker):
        self.window['-INFO-'].update('')
        self.window['-EARNINGS-'].update('')
        self.window['-FINVIZ-'].update('')

        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            filtered_info = self.filter_info(info)

            finviz_stock = finvizfinance(ticker.lower())
            finviz_info = finviz_stock.ticker_fundament()

            self.calculate_and_add_short_squeeze(filtered_info)
            self.display_info(filtered_info)
            self.display_finviz_info(finviz_info)

            #self.get_and_display_earnings_dates(ticker)

            margin_info = self.calculate_margin(float(filtered_info.get('dayLow', '0').replace('$', '').replace(',', '')))
            self.display_margin_info(margin_info)

        except Exception as e:
            self.window['-INFO-'].print(f"Error fetching data: {e}")


    def get_and_display_earnings_dates(self, ticker):

        url = f'https://www.sec.gov/cgi-bin/browse-edgar?type=10-&dateb=&owner=include&count=100&action=getcompany&CIK={ticker}'
        headerInfo = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headerInfo)
            if response.status_code == 200:
                soup = bs4.BeautifulSoup(response.text, 'html.parser')
                trElems = soup.select('tr')
                dateFind = re.compile(r'2\d{3}-\d{2}-\d{2}')
                dates = []
                

                for tr in trElems:

                    tdElems = tr.select('td')
                    if len(tdElems) == 5 and dateFind.search(tdElems[3].getText()) is not None:
                        date = tdElems[3].getText()
                        converted = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')
                        dates.append(converted)
                
                        

                if dates:
                    earnings_data = []
                    for date in dates:
                        earnings_date = datetime.datetime.strptime(date, '%m/%d/%Y')
                        earnings_date_formatted = earnings_date.strftime('%Y-%m-%d')
                        try:
                            print(earnings_date_formatted)
                            earnings = yf.Ticker(ticker).history(start="2022-06-02", end="2022-06-03",interval="1h")
                            print(earnings.head())
                            if not earnings.empty:
                                premarket_low = earnings['Low'].min()
                                premarket_high = earnings['High'].max()
                                earnings_data.append((date, premarket_low, premarket_high))
                            else:
                                earnings_data.append((date, 'N/A', 'N/A'))
                        except (KeyError, ValueError):
                            earnings_data.append((date, 'N/A', 'N/A'))

                    self.display_earnings_info(earnings_data)
                else:
                    self.window['-EARNINGS-'].print(f"No earnings dates found for {ticker}.\n")
            else:
                self.window['-EARNINGS-'].print("Failed to retrieve earnings dates. SEC website might be down or the ticker symbol is incorrect.\n")
        except requests.exceptions.RequestException as e:
            self.window['-EARNINGS-'].print(f"Failed to retrieve earnings dates: {e}\n")

    def filter_info(self, info):
        # Include the comprehensive list of keys you've specified
        desired_keys = [
            "country", "overallRisk", "dayLow", "dayHigh", "exDividendDate",
            "averageVolume", "averageVolume10days", "marketCap", "fiftyTwoWeekLow", "fiftyTwoWeekHigh",
            "fiftyDayAverage", "twoHundredDayAverage", "floatShares", "sharesOutstanding", "sharesShort",
            "sharesShortPriorMonth", "sharesShortPreviousMonthDate", "dateShortInterest",
            "sharesPercentSharesOut", "heldPercentInsiders", "heldPercentInstitutions",
            "shortPercentOfFloat", "52WeekChange", "lastDividendValue", "lastDividendDate", "currentPrice",
            "targetHighPrice", "targetLowPrice"
        ]
        filtered_info = {key: self.format_value(key, info.get(key, 'N/A')) for key in desired_keys}


        return filtered_info

    def calculate_and_add_short_squeeze(self, info):
        try:

            shares_short = float(info.get('sharesShort', 0).replace(",", ""))
            float_shares = float(info.get('sharesOutstanding', 0).replace(",", ""))
            if float_shares > shares_short > 0:
                short_squeeze_percentage = (shares_short / (float_shares - shares_short)) * 100
                print(f"{short_squeeze_percentage:.2f}%")
            else:
                info['shortSqueeze'] = "N/A"
        except Exception as e:
            info['shortSqueeze'] = "Error Calculating"


    def format_market_cap(self, market_cap):
        if market_cap >= 10**12:
            return f"${market_cap / 10**12:.2f}T"
        elif market_cap >= 10**9:
            return f"${market_cap / 10**9:.2f}B"
        elif market_cap >= 10**6:
            return f"${market_cap / 10**6:.2f}M"
        else:
            return f"${market_cap:.2f}"
        
    def format_value(self, key, value):
        formats = {
            "marketCap": self.format_market_cap,
            "dayLow": "${:.2f}".format,
            "dayHigh": "${:.2f}".format,
            "fiftyTwoWeekLow": "${:.2f}".format,
            "fiftyTwoWeekHigh": "${:.2f}".format,
            "fiftyDayAverage": "${:.2f}".format,
            "twoHundredDayAverage": "${:.2f}".format,
            "previousClose": "${:.2f}".format,
            "volume": "{:,}".format,
            "averageVolume": "{:,}".format,
            "averageVolume10days": "{:,}".format,
            "floatShares": "{:,}".format,
            "sharesOutstanding": "{:,}".format,
            "sharesShort": "{:,}".format,
            "sharesShortPriorMonth": "{:,}".format,
            "shortRatio": "{:.2f}".format,
            "sharesPercentSharesOut": lambda x: "{:.2f}%".format(x * 100),
            "heldPercentInsiders": lambda x: "{:.2f}%".format(x * 100),
            "heldPercentInstitutions": lambda x: "{:.2f}%".format(x * 100),
            "shortPercentOfFloat": lambda x: "{:.2f}%".format(x * 100),
            "52WeekChange": lambda x: "{:.2f}%".format(x * 100),
            "currentPrice": "${:.2f}".format,
            "targetHighPrice": "${:.2f}".format,
            "targetLowPrice": "${:.2f}".format,
        }
        if key in formats:
            return formats[key](value)
        return value

    def display_info(self, info):
        # Define keys and corresponding labels for plotting
        plot_keys = ['fiftyTwoWeekLow', 'fiftyTwoWeekHigh']
        plot_labels = ['52 Week Low', '52 Week High']

        # Extract values for plotting
        plot_values = [info.get(key, 0) for key in plot_keys]

        # Format values for plotting
        plot_values = [float(value.replace('$', '').replace(',', '')) for value in plot_values]

        # Plot the data horizontally
        plt.figure(figsize=(8, 4))
        plt.barh(plot_labels, plot_values, color=['blue', 'red'])
        plt.title('52 Week Low vs High')
        plt.ylabel('Price')
        plt.xlabel('Value ($)')
        plt.grid(True)

        for i, value in enumerate(plot_values):
            plt.text(value, i, f'${value:.2f}', va='center', ha='left')

        # plt.show()

        # Display other information
        for key, value in info.items():
            # Check if the key is not for plotting
            if key not in plot_keys:
                # Calculate padding for each line to center-align the values
                padding = max(len(key) for key in info.keys()) - len(key)
                formatted_key = f"{key}{' ' * padding}:"
                # Display the formatted key and value
                
                self.window['-INFO-'].print(f"{formatted_key} {value}", font=('Courier New', 11))


    def display_finviz_info(self, finviz_info):
        self.window['-FINVIZ-'].print("Finviz Data:")
        max_key_length = max(len(key) for key in ['Market Cap', 'Short Float', 'Shs Float'])
        for key in ['Market Cap', 'Short Float', 'Shs Float']:
            padding = max_key_length - len(key)
            formatted_value = finviz_info.get(key, 'N/A')
            formatted_line = f"{key}{' ' * padding}: {formatted_value}"
            self.window['-FINVIZ-'].print(formatted_line, font=('Courier New', 11))



    def calculate_margin(self, lowest_price):
        if lowest_price > 16.67:
            margin_percentage = 30
        elif lowest_price > 5:
            margin_percentage = (((1000 / lowest_price) * 5) / 1000) * 100
        elif lowest_price >= 2.5:
            margin_percentage = 100
        else:
            margin_percentage = (((1000 / lowest_price) * 2.5) / 1000) * 100
        
        margin_amount = (1000 * margin_percentage) / 100
        margin_amount_rounded = round(margin_amount)  # Round to the nearest whole dollar
        return f"{margin_percentage:.2f}% (${margin_amount_rounded})"  # Return the rounded value

    def display_margin_info(self, margin_info):
        self.window['-INFO-'].print(f"Margin Requirement: {margin_info}")

if __name__ == "__main__":
    app = StockInfoApp()
    app.run()
