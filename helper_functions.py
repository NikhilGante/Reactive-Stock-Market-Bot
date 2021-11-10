# helper code
"""
#submitting orders
api.submit_order(
    symbol='AMD',
    qty=1,
    side='sell',
    type='limit',
    time_in_force='opg',
    limit_price=20.50
)


# Get the last 100 of our closed orders
closed_orders = api.list_orders(
    status='closed',
    limit=100,
    nested=True  # show nested multi-leg orders
)

# Get only the closed orders for a particular stock
closed_aapl_orders = [o for o in closed_orders if o.symbol == 'AAPL']
print(closed_aapl_orders)


# Submit a market order and assign it a Client Order ID.
api.submit_order(
    symbol='AAPL',
    qty=1,
    side='buy',
    type='market',
    time_in_force='gtc',
    client_order_id='my_first_order'
)
# Get our order using its Client Order ID.
my_order = api.get_order_by_client_order_id('my_first_order')


# Check if the market is open now.
clock = api.get_clock()
print('The market is {}'.format('open.' if clock.is_open else 'closed.'))


# Check if AAPL is tradable on the Alpaca platform.
aapl_asset = api.get_asset('AAPL')
if aapl_asset.tradable:
    print('We can trade AAPL.')


# Get daily price data for AAPL over the last 5 trading days.
barset = api.get_barset('AAPL', 'day', limit=5)
aapl_bars = barset['AAPL']

# See how much AAPL moved in that timeframe.
week_open = aapl_bars[0].o
week_close = aapl_bars[-1].c
percent_change = (week_close - week_open) / week_open * 100
print('AAPL moved {}% over the last 5 days'.format(percent_change))    
"""