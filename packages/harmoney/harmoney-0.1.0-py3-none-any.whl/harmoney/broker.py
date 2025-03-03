import asyncio
import base64
from uvicorn import Config, Server
import fastapi
from uvicorn.config import LOG_LEVELS
import pickle as pkl
import uuid
from ._callSpec import _CallPacket, _ClientPacket

__all__ = ["runBroker"]

class _Broker:
    def __init__(self, pollingDelay=0.5) -> None:
        self.router = fastapi.APIRouter()
        self.router.add_api_websocket_route("/reg", self.registerRunner)
        self.router.add_api_route("/cliReq", self.clientRequest, methods=["POST"])
        self.taskQueue = asyncio.Queue()
        self.runnerCount=0
        self.returnDict = {}
        self.pollingDelay = pollingDelay


    async def registerRunner(self,  wsConnection: fastapi.WebSocket):
        await wsConnection.accept()
        await wsConnection.send_text(str(self.runnerCount))
        methods=await wsConnection.receive()
        methods = pkl.loads(base64.b64decode(methods["text"]))
        print(f"Runner Connected with ID: {self.runnerCount}, Methods: {methods['methods']}")
        self.runnerCount+=1
        while True:
            reqID, data  = await self.taskQueue.get()
            await wsConnection.send_bytes(pkl.dumps(data))
            retValue = await wsConnection.receive()
            self.returnDict[reqID] = retValue["bytes"]
            print(f"Tasks left: {self.taskQueue.qsize()}")

    async def clientRequest(self, data:_ClientPacket):
        reqID = uuid.uuid4().hex
        callPacket = pkl.loads(base64.b64decode(data.data))
        await self.taskQueue.put((reqID, callPacket))
        while reqID not in self.returnDict:
            await asyncio.sleep(self.pollingDelay)
        # await asyncio.sleep(1)
        returnValue = self.returnDict[reqID]
        return returnValue

def runBroker(host, port, pollingDelay=0.1):
    br = _Broker(pollingDelay=pollingDelay)
    app = fastapi.FastAPI()
    app.include_router(br.router)
    serverConf = Config(app = app, host=host,  port=port, log_level=LOG_LEVELS["warning"], ws_ping_interval=10, ws_ping_timeout=None)
    server = Server(config=serverConf)
    server.run()

# runBroker()
