import asyncio
import getpass
import json
import os
import random
import pprint
from consts import Tiles, TILES


import websockets
from mapa import Map


class Client:
    def __init__(self):

        # DO NOT CHANGE THE LINES BELLOW
        # You can change the default values using the command line, example:
        # $ NAME='arrumador' python3 client.py
        loop = asyncio.get_event_loop()
        SERVER = os.environ.get("SERVER", "localhost")
        PORT = os.environ.get("PORT", "8000")
        NAME = os.environ.get("NAME", getpass.getuser())
        loop.run_until_complete(self.agent_loop(f"{SERVER}:{PORT}", NAME))

    def is_valid_move(self, x, y):
        # verificar se dá pra fazer o move...
        pass

    async def agent_loop(self, server_address="localhost:8000", agent_name="student"):
        async with websockets.connect(f"ws://{server_address}/player") as websocket:

            # Receive information about static game properties
            await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
            msg = await websocket.recv()
            game_properties = json.loads(msg)

            # You can create your own map representation or use the game representation:
            print("----- MAP INFO -----")
            mapa = Map(game_properties["map"])
            print(mapa)
            # Retrieve map info
            print("----- ELEMENTS IN MAP -----")
            total_map_elems = mapa._map # lista com todos os elementos no mapa dado
            for elem in total_map_elems:
                print(elem) # vai mostrar quais TITLES tem boxes, paredes, keeper, (...)


            while True:
                try:
                    state = json.loads(
                        await websocket.recv()
                    )  # receive game state, this must be called timely or your game will get out of sync with the server

                    curr_x, curr_y = mapa.keeper
                    move = random.randrange(-1, 2, 2)
                    coord_pick = random.randrange(0, 2)  # 0 -> x || 1 -> y

                    if coord_pick == 0:
                        next_x = curr_x + move
                        next_y = curr_y
                    else:
                        next_y = curr_y + move
                        next_x = curr_x

                    if mapa.is_blocked((next_x, next_y)):
                        print("Invalid Move!!")
                        continue
                    else:
                        if move == 1 and coord_pick == 0:
                            key = "d"
                        elif move == 1 and coord_pick == 1:
                            key = "w"
                        elif move == -1 and coord_pick == 1:
                            key = "s"
                        else:
                            key = "a"

                        pprint.pprint(state)
                        print(Map(f"levels/{state['level']}.xsb"))
                        await websocket.send(
                            json.dumps({"cmd": "key", "key": key})
                        )  # send key command to server - you must implement this send in the AI agent

                except websockets.exceptions.ConnectionClosedOK:
                    print("Server has cleanly disconnected us")
                    return


if __name__ == "__main__":
    client = Client()
