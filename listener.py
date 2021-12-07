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
from data import *
import logging
import requests
from alpaca_trade_api.entity import (
  Watchlist
)



logging.basicConfig(
  filename="debug.log",
  filemode="w",
  level=logging.INFO,
  format="[%(asctime)s.%(msecs)03d] %(levelname)s > %(message)s",
  datefmt='(%M:%S)'
)
api = alpaca.REST()

print("Imports finished - Listener")

class Listener(object):
  baseurl = os.environ['APCA_API_BASE_URL']
  keyid = os.environ['APCA_API_KEY_ID']
  seckey = os.environ['APCA_API_SECRET_KEY']
  create = False

  def manual_watchlist(self):
    a = api.post("/watchlists",data={"name":"APCUI"+genrandstring()})
    self.watchlist = api.response_wrapper(a,Watchlist)

  def __init__(self, wl=None):
    if Listener.create:
      raise RuntimeError("Another listener has already been created.\nDue to Alpaca API constraints, please disable any active \nlisteners before recreating.")
    

    self.running = False
    print(api.get_watchlists())

    with open("wlsav.txt","r",encoding="utf-8") as save:
      defaultwatchlist = save.readline()
      defaultwatchlist.replace("\n","")
    
    wl = wl or defaultwatchlist

    if not wl:
      print("No watchlist, creating")
      self.manual_watchlist()
      with open("wlsav.txt","w+",encoding="utf-8") as file:
        file.write(self.watchlist.id)
    else:
      print(f"Attempting to get watchlist {wl}")
      try:
        self.watchlist = api.get_watchlist(wl)
      except Exception as e:
        print(f"Error while retrieving watchlist: {e}")
        self.manual_watchlist()
    print("Watchlist loaded.")

    print(self.watchlist.assets)

    for k in [k["symbol"] for k in api.list_positions()]:
      if k not in [k["symbol"] for k in self.watchlist.assets]:
        api.add_to_watchlist(self.watchlist.id, k)
    
    
    self.positions = api.list_positions()
    Listener.create = True
  
  def start(self):
    try: self.loop = asyncio.get_running_loop()
    except RuntimeError: print("No loop running, creating new one"); self.loop = asyncio.get_event_loop()
    self.running = True
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

      while self.running:
        msg = await connection.recv()
        print(literal_eval(msg))
        logging.info(msg)
        await self.update_for_ticker(None, False) # Buy or sell the ticker depending on its status
  
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

  def stop(self):
    self.running = False
    
  async def update_for_ticker(self, ticker, newval):
    pass
  
