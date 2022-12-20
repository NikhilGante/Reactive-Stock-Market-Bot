import private
import alpaca_trade_api as tradeapi
import matplotlib.pyplot as plt


# API Info for fetching data, portfolio, etc. from Alpaca
BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_API_KEY = private.api_key_id
ALPACA_SECRET_KEY = private.secret_key

# Instantiate REST API Connection
api = tradeapi.REST(key_id=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, base_url=BASE_URL, api_version='v2')
account = api.get_account()
print(account.id, account.equity, account.status)

# ------------ Graphing Apple Data -------------------
# Fetch Apple data from last 100 days
APPLE_DATA = api.get_barset('AAPL', 'day', limit=100).df

# Reformat data (drop multiindex, rename columns, reset index)
APPLE_DATA.columns = APPLE_DATA.columns.to_flat_index()
APPLE_DATA.columns = [x[1] for x in APPLE_DATA.columns]
APPLE_DATA.reset_index(inplace=True)
print(APPLE_DATA.head())

# Plot stock price data
plot = APPLE_DATA.plot(x="time", y="close", legend=False)
plot.set_xlabel("Date")
plot.set_ylabel("Apple Close Price ($)")
plt.show()