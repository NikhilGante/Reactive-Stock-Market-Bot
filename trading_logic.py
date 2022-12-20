from math import sin, cos
class trade_algo:
    def __init__(self, lst):
        self.starting_capital = 1000
        self.cash = self.starting_capital
        self.lst = lst
        self.last_buy_price = lst[0]
        self.last_sell_price = lst[0]
        self.lst_len = len(lst)
        self.current_investment = 0 # how much money is currently invested
        self.index = 0 # iterator of for loop
        self.done = False
        self.trades = []
        self.buffer_size = 0.5 # how much the new share must exceed the old share
        # self.buy = False
        # self.sell = False

    def sell(self):
        self.last_sell_price = self.lst[self.index]
        self.cash += self.last_sell_price
        self.trades.append(("SELL",self.last_sell_price))
        # self.last_buy_price = 0  # resets last_buy_price for profit calculation 
        self.current_investment = 0 # how much our current stock is worth


    def buy(self):
        self.last_buy_price = self.lst[self.index]
        self.cash -= self.last_buy_price
        self.trades.append(("BUY",self.last_buy_price))


    def find_peak(self):
        last_read_was_greatest = False
        greatest = self.last_buy_price # searches for stock prices greater than last buy

        while True: # doesn't exceed length of lst
            if self.index >= self.lst_len or self.done:
                self.done = True
                return
            # NOTE: greater than or equal to is necessary to make sure to not count a false peak
            self.current_investment = self.lst[self.index] # how much our current stock is worth
            if self.lst[self.index] >= greatest:
                greatest = self.lst[self.index]
                if greatest - self.last_buy_price > self.buffer_size: # potential peak found
                    last_read_was_greatest = True
            elif last_read_was_greatest:    # sells exactly one reading after peak
                self.sell()
                return
            else:   # resets last_read_was_greatest to false if stock rises again
                last_read_was_greatest = False
            self.index += 1
        # self.index -= 1 # moves index back for find_trough to scan for immediate trough
        
        

    def find_trough(self):
        last_read_was_least = False
        least = self.last_sell_price # searches for stock prices less than last sell
        while True: # doesn't exceed length of lst
            if self.index >= self.lst_len or self.done:
                self.done = True
                return
            # NOTE: less than or equal to is necessary to make sure to not count a false trough
            if self.lst[self.index] <= least:
                least = self.lst[self.index]
                if self.last_sell_price - least > self.buffer_size: # potential trough found
                    last_read_was_least = True
            elif last_read_was_least:    # buys exactly one reading after trough
                self.buy()
                return
            else:   # resets last_read_was_least to false if stock dips again
                last_read_was_least = False
            self.index += 1
        # self.index -= 1 # moves index back for find_peak to scan for immediate peak
        

    def run(self):
        # self.buy()
        while self.index < self.lst_len or not self.done: # doesn't exceed length of lst
            self.find_trough()
            self.find_peak()





# daily
lst = [
    136.60, 136.67, 136.02, 136.22, 137.38, 137.63, 136.64, 135.89, 135.31, 135.45, 135.39,
    134.88, 135.07, 134.94, 135.14, 135.25, 134.90, 135.12, 135.14, 134.90, 134.72, 135.03,
    135.14, 134.60, 134.66, 134.97, 135.03, 134.83, 134.42, 134.60, 134.54, 134.77, 134.65,
    134.58, 134.80, 134.84, 134.88, 134.85, 135.13, 134.72, 134.62, 134.45, 134.32, 134.19,
    134.18, 134.19, 134.15, 134.02, 134.02, 134.17, 134.03, 134.01, 134.15, 134.19, 134.30,
    134.24, 134.25, 134.44, 134.38, 134.01, 134.00, 133.78, 133.83, 133.98, 134.13, 134.32,
    134.36, 134.18, 134.74, 134.61, 134.81, 134.88, 135.02, 135.10, 135.03, 134.97, 134.76,
]
# lst = [
#     143.19, 143.87, 143.98, 144.00, 143.84, 144.14, 143.84, 144.04, 144.08, 143.94, 143.76,
#     143.53, 143.77, 143.28, 143.12, 143.17, 143.76, 143.30, 143.30, 142.90, 143.00, 142.84,
#     142.97, 142.64, 142.86, 143.30, 143.07, 143.30, 142.99, 140.14, 143.18, 143.99, 144.72,
#     144.47, 144.44, 144.43, 144.07, 144.06, 143.52, 143.58, 143.60, 143.39, 143.17, 142.81,
#     143.15, 141.86, 141.79, 141.54, 142.01, 142.31, 142.50, 141.85, 141.88, 141.88, 142.66,
#     141.97, 141.80, 141.44, 141.24, 139.76, 139.66, 139.90, 139.58, 140.14, 140.12, 140.02,
#     140.42, 140.44, 140.46, 140.38, 140.42, 140.91
# ]
# lst= []
# def sinusoidal(x):
#   return 3*sin(5.3*cos(1.7* sin(3.6*cos(x))))
# lst = []
# for i in range(0, 50):
#   lst.append(sinusoidal(i/10))
# for i,j in enumerate(lst):
#   print(f"{i/10}, {j}")

obj = trade_algo(lst)

obj.run()
print("total: ", obj.cash)
print("Current: ", obj.current_investment)
print(obj.trades)
print("len", len(obj.trades))
print("Last Buy Price:", obj.last_buy_price)
print("Totes Profit: ", obj.cash + obj.current_investment - obj.starting_capital)