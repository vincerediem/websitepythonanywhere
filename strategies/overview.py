import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
from pytz import timezone
import plotly.graph_objs as go
import plotly.subplots as sp
import yfinance as yf

API_KEY = 'PK3ABIZYDFUBONQF8FCW'
SECRET_KEY = 'sinlF6QYXaoVKA6Y6WFqTyx8zfYyuwrpwgO2WL7v'
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL, api_version='v2')

index_list = ["SPY", "QQQ", "DIA"]
stock_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "V", "NVDA", "META", "UNH", "LLY", "JPM", "XOM", "JNJ", "PG"]

# Define a color mapping for each index
color_mapping = {
    "SPY": "blue",
    "QQQ": "red",
    "DIA": "green"
}

def calculate_ytd_percent_change(historical_data):
    first_close_price = historical_data['close'][0]
    last_close_price = historical_data['close'][-1]
    ytd_percent_change = ((last_close_price - first_close_price) / first_close_price) * 100
    return ytd_percent_change

def calculate_5y_percent_change(historical_data):
    first_close_price = historical_data['close'][0]
    last_close_price = historical_data['close'][-1]
    five_year_percent_change = ((last_close_price - first_close_price) / first_close_price) * 100
    return five_year_percent_change

def create_stock_dataframe(stock_list):
    stock_data = []  # List to store stock data
    
    for stock in stock_list:
        historical_data = get_historical_data(stock)
        
        ytd_percent_change = calculate_ytd_percent_change(historical_data)
        five_year_percent_change = calculate_5y_percent_change(historical_data)
        
        last_close_price = historical_data['close'].iloc[-1]
        
        # Append stock data to the list including the last closing price
        stock_data.append([stock, last_close_price, ytd_percent_change, five_year_percent_change])
    
    # Create a DataFrame to store the stock data
    df = pd.DataFrame(stock_data, columns=["Stock", "Last Close Price", "YTD % Change", "5Y % Change",])

    df = df.reset_index(drop=True)

    styled_df = df.style.set_properties(**{'text-align': 'center'})
    styled_df = styled_df.set_table_styles([{
        'selector': 'th',
        'props': [('background-color', 'lightgrey'), ('text-align', 'center')]
    }])
    
    # Format numeric values with two decimal places
    styled_df = styled_df.format({'YTD % Change': '{:.2f}', '5Y % Change': '{:.2f}', 'Last Close Price': '{:.2f}'})

    return styled_df

def plot_last_year_prices(index_list):
    start_date = (datetime.datetime.now(timezone('America/New_York')) - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now(timezone('America/New_York')) - datetime.timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    fig = sp.make_subplots(rows=2, cols=1, subplot_titles=["1yr Close Prices", "1yr Percent Change"])

    ytd_percent_increase = {}  # Dictionary to store YTD percent increase for each stock
    
    legend_items = set()  # Set to store legend items and prevent duplicates
    
    for stock in index_list:
        historical_data = get_historical_data(stock, start_date, end_date)
        
        # Calculate YTD percent increase for each day in the year
        ytd_percent_increase[stock] = [(historical_data['close'][i] - historical_data['close'][0]) / historical_data['close'][0] * 100 for i in range(len(historical_data))]
        
        # Use the color mapping for both price and YTD percent increase traces
        trace_price = go.Scatter(x=historical_data.index, y=historical_data['close'], mode='lines', name=stock, hoverinfo='x+y+name', line=dict(color=color_mapping[stock]))
        fig.add_trace(trace_price, row=1, col=1)
        
        trace_ytd = go.Scatter(x=historical_data.index, y=ytd_percent_increase[stock], mode='lines', name=stock, hoverinfo='x+y+name', line=dict(color=color_mapping[stock]))
        fig.add_trace(trace_ytd, row=2, col=1)
    
    
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="1yr Percent Increase (%)", row=2, col=1)

    fig.add_hline(y=0, line_dash="dash", line_color="red", line_width=1.5, row=2, col=1)

    fig.update_layout(height=600, width=800, title_text='', margin=dict(l=0, r=0, t=30, b=30))

    # Create a single legend on the right
    fig.update_layout(legend=dict(orientation="v", x=1.05, y=0.5, traceorder="normal"))

    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return plot_html

def get_historical_data(stock, start_date=None, end_date=None):
    if start_date is None:
        start_date = (datetime.datetime.now(timezone('America/New_York')) - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = (datetime.datetime.now(timezone('America/New_York')) - datetime.timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    bars = api.get_bars(stock, tradeapi.rest.TimeFrame.Day, start_date, end_date, limit=None, adjustment='raw').df
    return bars

if __name__ == '__main__':
    plot_last_year_prices(index_list)

    stock_dataframe = create_stock_dataframe(stock_list)
    # Print the DataFrame
    print(stock_dataframe)