"""
Title: Alpaca Trade UI
Writers: Ike Yang and Nikhil Gante

A user interface for viewing automated trading progress on the Alpaca API.

# NOTE: The API limits call amounts to 200 per minute.
# Any calls after this point will return 404 errors.

Structure:
Uses websockets to listen to stock changes and provide updates to client
Uses standard HTTP to perform portfolio actions
Object-based framework for "Algos"; each algo is an object which the client evaluates upon events and "asks" for what to do
"""

import curses
from listener import Listener as ls
from ticker import getTradeHistory, make_money
import logging
from time import sleep
from flask import Flask, make_response, jsonify
import threading

app = Flask(__name__)

print("AlpacaTradeUI Test Version")
logging.basicConfig(
  filename="debug.log",
  filemode="w",
  level=logging.INFO,
  format="[%(asctime)s.%(msecs)03d] %(levelname)s > %(message)s",
  datefmt='(%M:%S)'
)

mainlis = ls(make_money(None, None, cap_alloc=15000, b_sense=0, s_sense=0, buff_size=0.35, buffer_enable=True), addtickers=["AAPL", "NVDA", "AMD", "MSFT", "KRA"])

fserver = threading.Thread(target=lambda: app.run(host='0.0.0.0', debug=True, use_reloader=False), daemon=True)

@app.route("/", methods=['GET'])
def processreq():
  # If it's a GET method, it's a get request for the JSON data of the most recent trades and the
  resp = make_response(jsonify(
    {
      "watchlist" : list([x["symbol"] for x in mainlis.watchlist.assets]),
      "trades": getTradeHistory()
    }
  ), 200)
  resp.headers["Access-Control-Allow-Origin"] = "*"
  resp.headers["content-type"] = "application/json"
  return resp

if __name__ == "__main__":
  fserver.start()
  mainlis.start()


  






