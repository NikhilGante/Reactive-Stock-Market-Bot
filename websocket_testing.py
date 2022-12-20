import private
import alpaca_trade_api
import asyncio
import websockets

# connects to websocket

websocket_path = "wss://stream.data.alpaca.markets/v2/iex"  # iex because we are using the free API

async def hello():
    async with websockets.connect(websocket_path) as websocket:

        name = input("What's your name? ")
        await websocket.send(name)
        print("> {}".format(name))

        greeting = await websocket.recv()
        print("< {}".format(greeting))

asyncio.get_event_loop().run_until_complete(hello())