
import alpaca_trade_api as alpaca
from data import readTradeData, writeTradeData

trades = readTradeData()

def getTradeHistory():
  return trades

class make_money:
  def __init__(self, rest: alpaca.REST, tckr, cap_alloc=1000, b_sense=9, s_sense=5, buffer_enable=False, buff_size=0.5):
    self.starting_capital = cap_alloc
    self.cash = cap_alloc
    self.last_action_price = 0
    self.last_action_qty = 0
    self.last_action = "Sell"
    self.tckr = tckr
    
    self.api = rest
    
    self.s_sense = s_sense
    self.b_sense = b_sense

    self.done = False
    self.tradesFromLastAction = []
    self.buffer_size = buff_size
    self.pendingOrderFill = None
    self.last_price = 9999999999
    self.resistance = 0
    self.support = 9999999999
    self.move_buffer = b_sense
    self.buffer_enable = buffer_enable
    print("============================")
    print(f"Trading {tckr}")
    print(f"Allocated capital: ${cap_alloc}")
    print(f"Buy sensitivity: {b_sense}")
    print(f"Sell sensitivity: {s_sense}")
    print(f"Force Profits: {buffer_enable}")
    print("============================")

  
    global trades
    writeTradeData(trades)

  def algcopy(self, tckr):
    return make_money(self.api, tckr, cap_alloc = self.starting_capital, b_sense = self.b_sense, s_sense = self.s_sense, buffer_enable = self.buffer_enable, buff_size = self.buffer_size)

  def checkOrderStatus(self):
    global trades
    if not self.pendingOrderFill:
      return
    else:
      repons = self.api.get_order_by_client_order_id(self.pendingOrderFill)
      if repons.filled_avg_price:  # Order successfully filled
        self.last_action_price = float(repons.filled_avg_price)
        self.last_action_qty = int(repons.qty)
        if self.last_action == "Sell":
          self.cash += self.last_action_price * self.last_action_qty
        elif self.last_action == "Buy":
          self.cash -= self.last_action_price * self.last_action_qty
        self.pendingOrderFill = None
        self.last_price = self.last_action_price
        print(f"(!) Traded <{self.last_action} {self.last_action_qty}x {self.tckr} @ {self.last_action_price}")
        trades = [{
          "action": self.last_action,
          "qty": self.last_action_qty,
          "ticker": self.tckr,
          "price": self.last_action_price
        }] + trades[:5]

  def sell(self):
    self.last_action = "Sell"
    order = self.api.submit_order(
      symbol = self.tckr,
      qty = self.last_action_qty,
      side = "sell",
      type= "market",
      time_in_force = "day"
    )

    self.pendingOrderFill = order.client_order_id
    """
    self.cash += self.last_price * self.last_action_qty
    print(f"Sell {self.tckr} x{self.last_action_qty} at {self.last_price}")
    self.last_action_price = self.last_price
    print(f"Now ${self.cash}")
    """

  def buy(self):
    self.last_action = "Buy"
    
    order = self.api.submit_order(
      symbol = self.tckr,
      qty = self.last_action_qty,
      side = "buy",
      type= "market",
      time_in_force = "day"
    )
    
    self.pendingOrderFill = order.client_order_id
    """
    self.cash -= self.last_price * self.last_action_qty
    print(f"Buy {self.tckr} x{self.last_action_qty} at {self.last_price}")
    self.last_action_price = self.last_price
    print(f"Now ${self.cash}")
    """

  def find_peak(self):
    if self.last_price >= self.resistance:
      self.resistance = self.last_price
      self.move_buffer = self.s_sense
    elif self.move_buffer <= 0 and (abs(self.last_price - self.last_action_price) > self.buffer_size or not self.buffer_enable):
      self.sell()
      self.move_buffer = self.b_sense
      self.resistance = 0
    else:
      self.move_buffer -= 1
  
  def find_trough(self):
    if self.last_price <= self.support:
      self.support = self.last_price
      self.move_buffer = self.b_sense
    elif self.move_buffer <= 0:
      self.last_action_qty = self.cash // self.last_price
      self.buy()
      self.move_buffer = self.s_sense
      self.support = 999999999
    else:
      self.move_buffer -= 1

  def eval(self, newval):
    # self.buy()
    self.last_price = newval;
    self.checkOrderStatus()
    if not self.pendingOrderFill:
      if self.last_action == "Buy":
        self.find_peak()
      else:
        self.find_trough()