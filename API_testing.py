import private
import alpaca_trade_api

# The endpoint tells the API we are accessing the paper trading page specifically
endpoint = "https://paper-api.alpaca.markets"

# sends a request to the alpaca trade api to get an API object
api = alpaca_trade_api.REST(private.api_key_id, private.secret_key, endpoint)

# saves account object returned from the api method
account = api.get_account()

print(account.status)


