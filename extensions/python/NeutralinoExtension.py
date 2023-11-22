# NeutralinoExtension
#
# A Python extension engine for Neutralino.
#
# Requirements:
# pypy -m pip install --no-binary :all: simple-websocket
# pypy -m pip install --no-binary :all: simple-websocket-server
#
# (c)2023 Harald Schneider

from argparse import *
import uuid, json, time, asyncio, sys, os, signal, subprocess
from simple_websocket import *
from queue import Queue


class NeutralinoExtension:

    def __init__(self, debug=False):

        self.version = "1.1.5"

        parser = ArgumentParser()
        parser.add_argument('--nl-port')
        parser.add_argument('--nl-token')
        parser.add_argument('--nl-extension-id')
        args = parser.parse_args()

        self.debug = debug
        self.debugTermColors = True             # Use terminal colors
        self.debugTermColorIN = "\033[32m"      # Green: All incoming events, except function calls
        self.debugTermColorCALL = "\033[91m"    # Red: Incoming function calls
        self.debugTermColorOUT = "\033[33m"     # Yellow: Outgoing events

        self.port = args.nl_port
        self.token = args.nl_token
        self.idExtension = args.nl_extension_id
        self.urlSocket = f"ws://127.0.0.1:{self.port}?extensionId={self.idExtension}"
        self.qSend = Queue()

        self.termOnWindowClose = True   # Terminate on windowCloseEvent message
        self.debugLog(f"{self.idExtension} running on port {self.port}")

    def sendMessage(self, event, data):
        """
        Add a data package to the sending queue.
        Triggers an event in the parent app.
        :param event: Event name as string
        :param data: Event data
        :return: --
        """

        d = {
              "id": str(uuid.uuid4()),
              "method": 'app.broadcast',
              "accessToken": self.token,
              "data": {
                    "event": event,
                    "data": data
                }
            }

        self.qSend.put(json.dumps(d))

    async def run(self, onReceiveMessage):
        """
        Socket-handler main loop. Sends and receives messages.
        :param onReceiveMessage: Callback for incoming messages
        :return: --
        """

        self.socket = await AioClient.connect(self.urlSocket)
        try:
            while True:

                if self.qSend.qsize() > 0:
                    #
                    # Send

                    msg = self.qSend.get()
                    await self.socket.send(msg)
                    self.debugLog(msg, 'out')
                else:
                    #
                    # Receive

                    msg = await self.socket.receive()
                    self.debugLog(msg, 'in')

                    try:
                        if self.termOnWindowClose:
                            d = json.loads(msg)
                            if d['event'] == 'windowClose' or d['event'] == 'appClose':
                                pid = os.getpid()
                                os.kill(pid, signal.SIGTERM)
                                return
                    except:
                        pass

                    try:
                        msg = json.loads(msg)
                        onReceiveMessage(msg)
                    except:
                        pass

        except (KeyboardInterrupt, EOFError, ConnectionClosed):
            await self.socket.close()

    def parseFunctionCall(self, d):
        """
        Extracts method and parameters from a data package.
        Handles JSON and string parameters.
        Data package struct:
        {
          "data":{
            "function":"ping",
            "parameter":"Python says PONG!"
          },
          "event":"runPython"
        }
        :param d: Data package as dict.
        :return: Tuple function, parameter
        """

        f = d['data']['function']
        p = d['data']['parameter']

        # p can be JSON or string
        #
        try:
            d = json.loads(p)
        except:
            d = p

        return f, p

    def debugLog(self, msg, tag="info"):
        """
        Log messages to terminal.
        :param msg: Message string
        :param tag: Type of log entry
        :return: --
        """

        cIN = ''
        cCALL = ''
        cOUT = ''
        cRST = ''

        if self.debugTermColors:
            cIN = self.debugTermColorIN
            cCALL = self.debugTermColorCALL
            cOUT = self.debugTermColorOUT
            cRST = "\033[0m"

        if not self.debug:
            return

        if tag == 'in':
            if 'runPython' in msg:
                print(f"{cCALL}IN:  {msg}{cRST}")
            else:
                print(f"{cIN}IN:  {msg}{cRST}")
            return

        if tag == 'out':
            print(f"{cOUT}OUT: {msg}{cRST}")
            return

        print(msg)
