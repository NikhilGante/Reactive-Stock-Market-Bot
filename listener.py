"""
Title: Alpaca Trade Ui
Writers: Ike Yang and Nikhil Gante

A user interface for viewing automated trading progress on the Alpaca API.

# NOTE: The API limits call amounts to 200 per minute.
# Any calls after this point will return 404 errors.

Structure:
Uses websockets to listen to stock changes and provide updates to client
Uses standard HTTP to perform portfolio actions
Object-based framework for "Algos"; each algo is an object which the client evaluates upon events and "asks" for what to do
"""
import asyncio
import websockets as ws
import alpaca_trade_api as alpaca
import os
from ast import literal_eval
from data import genrandstring, serializedict
import logging
from alpaca_trade_api.entity import (
  Watchlist
)
import datetime

api = alpaca.REST()

class Listener(object):
  baseurl = os.environ['APCA_API_BASE_URL']
  keyid = os.environ['APCA_API_KEY_ID']
  seckey = os.environ['APCA_API_SECRET_KEY']
  create = False

  def __init__(self, algo, wl=None, addtickers=[]):
    if Listener.create:
      raise RuntimeError("Another listener has already been created.\nDue to Alpaca API constraints, please disable any active \nlisteners before recreating.")

    self.running = False

    with open("wlsav.txt","r",encoding="utf-8") as save:
      defaultwatchlist = save.readline()
      defaultwatchlist.replace("\n","")
    
    wl = wl or defaultwatchlist

    if not wl:
      print("Creating new watchlist")
      self.manual_watchlist()
    else:
      print(f"Attempting to get Watchlist <{wl}>")
      try:
        self.watchlist = api.get_watchlist(wl)
      except Exception as e:
        print(f"Error while retrieving watchlist: {e}")
        self.manual_watchlist()
    
    print("Watchlist loaded.")
    with open("wlsav.txt","w+",encoding="utf-8") as file:
        file.write(self.watchlist.id)
    for k in [x.symbol for x in api.list_positions()]:
      if k not in [x["symbol"] for x in self.watchlist.assets]:
        self.watchlist = api.add_to_watchlist(self.watchlist.id, k)
    
    for k in addtickers:
      if k not in [x["symbol"] for x in self.watchlist.assets]:
        self.watchlist = api.add_to_watchlist(self.watchlist.id, k)

    print(f"{self.watchlist.name}\n=======================")
    print(f"Watchlist ID: {self.watchlist.id}")
    print(f"Total # of tickers watched: {len(self.watchlist.assets)}\n=======================")
    
    self.positions = api.list_positions()
    Listener.create = True
    self.basealgo = algo
    self.basealgo.api = api
    
    self.algos = {}
    self.sttime = 0
    self.entime = 0
    self.starteq = api.get_account().equity
    self.performance = {}
  
  def start(self):
    try: self.loop = asyncio.get_running_loop()
    except RuntimeError: self.loop = asyncio.get_event_loop()
    self.running = True
    self.sttime = datetime.datetime.now()
    asyncio.run(self.listen())

  async def listen(self):
    async with ws.connect("wss://stream.data.alpaca.markets/v2/iex") as connection:
      connect = await connection.recv()
      logging.info(connect)
      connect = await connection.send(serializedict(
        {"action": "auth", "key": os.environ['APCA_API_KEY_ID'], "secret": os.environ['APCA_API_SECRET_KEY']}
      )) # Authentication
      logging.info(connect)
      
      # Setup subscriptions for tickers

      if self.watchlist.assets:
        connect = await connection.send(serializedict(
        {"action": "subscribe", "trades": [k['symbol'] for k in self.watchlist.assets]}
      ))

      logging.info(connect)

      self.algos = {}
      for k in self.watchlist.assets:
        self.algos[k['symbol']] = self.basealgo.algcopy(k['symbol'])
      
      while self.running:
        msg = literal_eval(await connection.recv())[0]
        if msg.get("T", None) == "t":
          self.update_for_ticker(msg["S"], msg["p"])
        else:
          logging.info(msg)

  def manual_watchlist(self):
    a = api.post("/watchlists",data={"name":"APCUI"+genrandstring()})
    self.watchlist = api.response_wrapper(a,Watchlist)
  
  def add_ticker(self, tickername):
    try:
      print(api.get_asset(tickername))
      if tickername not in [k["symbol"] for k in self.watchlist.assets]:
        print("Not in watchlist, adding.")
        self.watchlist = api.add_to_watchlist(self.watchlist.id, tickername)
    except Exception as e:
      print(e)
  
  def remove_ticker(self, tickername):
    try:
      print(api.get_asset(tickername))
      if tickername in [k["symbol"] for k in self.watchlist.assets]:
        print("Removing from watchlist.")
        self.watchlist = api.delete_from_watchlist(self.watchlist.id, tickername)
    except Exception as e:
      print(e)

  async def stop(self):
    self.running = False
    self.entime = datetime.datetime.now()
    api.close_all_positions()
    temp = api.get_account().equity
    self.performance = {
      "final": temp,
      "sttime": self.sttime.strfttime("%b %d %H:%M:%S"),
      "entime": self.entime.strfttime("%b %d %H:%M:%S"),
      "runtime": (self.entime-self.sttime).strfttime("%d:%H:%M:%S"),
      "difference": temp-self.starteq,
      "percent": (temp-self.starteq)/self.starteq * 100
    }
    
  def update_for_ticker(self, ticker, newval):
    self.algos[ticker].eval(newval)