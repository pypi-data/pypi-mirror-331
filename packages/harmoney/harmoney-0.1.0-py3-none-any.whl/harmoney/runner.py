import base64
from typing import Any, Dict
# from fastapi import WebSocketException
from websockets.asyncio import client as WSC
from websockets.exceptions import WebSocketException
import asyncio
import pickle as pkl
from ._callSpec import _CallPacket

__all__ = ["startRunner"]

async def _send(funcMap: Dict[str, Any], url):
    counter=0
    async with WSC.connect(url, open_timeout=None, ping_interval=10, ping_timeout=None ) as w:
        try:
            id = await w.recv()
            id = int(id)
            print(f"Starting Runner, ID: {id}")
            await w.send(base64.b64encode(pkl.dumps({"methods":list(funcMap.keys())})).decode("utf-8"))
            while True:
                counter+=1
                packetBytes=await w.recv()
                callPk:_CallPacket = pkl.loads(packetBytes)
                print("-"*50 + f"\nRunning: {callPk.procedure}\nArgs: {callPk.data}\nCounter: {counter}\n" + "-"*50)
                funcOutput = funcMap[callPk.procedure](**callPk.data)
                await w.send(base64.b64encode(pkl.dumps(funcOutput)))
        except WebSocketException as e:
            print(f"Closing Conncetion with Broker, total call count: {counter}")
            await w.close()

def startRunner(funcMapping, host, port):
    asyncio.run(_send(funcMapping, f"ws://{host}:{port}/reg"))
