import time
import requests as req
from ._callSpec import _CallPacket
import pickle as pkl
import base64
from threading import Thread

__all__ = ["Client"]

class Client:
    def __init__(self, host, port) -> None:
        self._url = f"http://{host}:{port}/cliReq"
        self.tasks = []

    def singleCall(self, function, **kwargs):
        callPacket = _CallPacket(procedure=function, data=kwargs)
        payload = {"data": base64.b64encode(pkl.dumps(callPacket)).decode("utf-8")}
        resp = req.post(self._url, json=payload)
        return pkl.loads(base64.b64decode(resp.text))

    def addCall(self, function, **kwargs):
        self.tasks.append((function, kwargs))
        print(f"Total in Queue: {len(self.tasks)}")

    def runAllCalls(self, callDelay=0.01):
        if len(self.tasks) == 0:
            return []
        self.returnValues = [0]*len(self.tasks)
        self.done = [0] * len(self.tasks)
        for callIDX in range(len(self.tasks)):
            t = Thread(target=self._threadWorker, args=[callIDX, self.tasks[callIDX]])
            t.start()
            time.sleep(callDelay)
        while not all(self.done):
            time.sleep(1)
        self.tasks = []
        return self.returnValues

    def _threadWorker(self, callIDX, payload):
        print(callIDX, payload)
        ret = self.singleCall(function=payload[0], **payload[1])
        self.returnValues[callIDX] = ret
        self.done[callIDX] =1
