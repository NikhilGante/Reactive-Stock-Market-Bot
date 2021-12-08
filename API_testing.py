import private
import alpaca_trade_api


# print(api.list_assets(status = 'active'))
# print(account.__doc__)
# print(api.get_barset('AAPL', 'day', limit=5)['AAPL'])

# BOT TESTING

class trader:
    def __init__(self, lst):
        self.starting_capital = 100000
        self.cash = self.starting_capital
        self.lst = lst
        self.last_buy_price = lst[0]
        self.last_sell_price = lst[0]
        self.lst_len = len(lst)
        self.current_investment = 0 # how much money is currently invested
        self.index = 0 # iterator of for loop
        self.done = False # if we are finished trading
        self.trades = []
        self.buffer_size = 0.50 # how much the new share must exceed the old share
        
        self.order_num = 0 # keeps track of how many orders have been executed

        # API specific variables
        self.symbol = 'AAPL' # which stock we are trading, will be exposed to the user later
        self.trade_quantity = 1 # how many stocks we buy/sell per trade, will be exposed to the user later
        self.current_order = None # to let us wait until our current order has been processed
        
        # The endpoint tells the API we are accessing the paper trading page specifically
        endpoint = "https://paper-api.alpaca.markets"

        # sends a request to the alpaca trade api to get an API object
        self.api = alpaca_trade_api.REST(private.api_key_id, private.secret_key, endpoint)

        # saves account object returned from the api method
        self.account = self.api.get_account()

        print("Account status:", self.account.status)
        
        # self.buy = False
        # self.sell = False

    def order(self, order_type): # executes either a buy or sell
        self.order_num += 1
        while True: # waits for current order to be fulfilled
            self.current_order = self.api.submit_order(
                symbol = self.symbol,
                qty = self.trade_quantity,
                side = order_type,
                type = 'market', # order attempts to execut immediately
                time_in_force = 'gtc', # "good-til-closed" i.e. order stays open until fulfilled
                client_order_id = order_type + str(self.order_num) # descriptive order ID ex. "sell2" or "buy4" 
            )
            print("ORDER ATTEMPTED", order_type + str(self.order_num))
            if not self.current_order: # order has been fulfilled
                break
            print("waiting")
        print("ORDER COMPLETE", order_type + str(self.order_num))
            

    def sell(self):
        # the current investment is amount we just purchased the stock for
        self.current_investment = self.last_sell_price
        self.last_sell_price = self.lst[self.index]
        self.cash += self.last_sell_price
        self.trades.append(("SELL", self.last_sell_price))
        print(self.trades)
        #Actual API interaction
        self.order('buy')
        # self.current_order
        

    def buy(self):
        # the current investment is amount we just purchased the stock for
        self.current_investment = 0.0
        self.last_buy_price = self.lst[self.index]
        self.cash -= self.last_buy_price
        self.trades.append(("BUY", self.last_buy_price))
        print(self.trades)
        self.order('sell')
        # Actual API interaction

    def find_peak(self):
        last_read_was_greatest = False
        greatest = self.last_buy_price # searches for stock prices greater than last buy

        while True: # doesn't exceed length of lst
            if self.index >= self.lst_len or self.done:
                self.done = True
                return
            # NOTE: greater than or equal to is necessary to make sure to not count a false peak
            if self.lst[self.index] >= greatest:
                greatest = self.lst[self.index]
                if greatest - self.last_buy_price > self.buffer_size: # potential peak found
                    last_read_was_greatest = True
            elif last_read_was_greatest and self.clock.is_open:    # sells exactly one reading after peak
                self.sell()
                return
            else:   # resets last_read_was_greatest to false if stock rises again
                last_read_was_greatest = False
            self.index += 1
        # self.index -= 1 # moves index back for find_trough to scan for immediate trough
        
    def find_trough(self):
        last_read_was_least = False
        least = self.last_sell_price # searches for stock prices greater than last sell

        while True: # doesn't exceed length of lst
            if self.index >= self.lst_len or self.done:
                self.done = True
                return
            # NOTE: less than or equal to is necessary to make sure to not count a false trough
            if self.lst[self.index] <= least:
                least = self.lst[self.index]
                if self.last_sell_price - least > self.buffer_size: # potential trough found
                    last_read_was_least = True
            # buys exactly one reading after trough, if market is open
            elif last_read_was_least and self.clock.is_open and self.cash > self.lst[self.index]:
                self.buy()
                return
            else:   # resets last_read_was_least to false if stock dips again
                last_read_was_least = False
            self.index += 1
        # self.index -= 1 # moves index back for find_peak to scan for immediate peak
        

    def run(self):
        # Check if AAPL (or our target stock) is tradable on the Alpaca platform.
        aapl_asset = self.api.get_asset(self.symbol)
        if aapl_asset.tradable:
            print(f'We can trade {self.symbol}.')
        else:
            print(f"We can't trade {self.symbol}, EXITED.")
            return
        while self.index < self.lst_len or not self.done: # doesn't exceed length of lst
            self.clock = self.api.get_clock()    # to see if market is currently open
            self.find_trough()
            self.find_peak()


lst = [
    141.24, 140.50, 140.64, 140.21, 139.90, 139.66, 139.76, 140.07, 139.58, 139.73, 139.59,
    139.66, 139.96, 139.74, 139.96, 139.97, 139.84, 139.80, 139.90, 139.90, 139.84, 139.74,
    139.64, 139.58, 139.39, 139.42, 139.58, 139.91, 139.92, 140.14, 139.92, 139.92, 140.02,
    139.93, 140.05, 140.12, 140.00, 139.92, 140.05, 140.02, 139.91, 140.02, 140.06, 140.12
]

obj = trader(lst)

obj.run()
print("total:", obj.cash)
print("current_investment:", obj.current_investment)
print(obj.trades)
print("Number of trades:", len(obj.trades))
print("totes profit:", obj.cash + obj.current_investment - obj.starting_capital)