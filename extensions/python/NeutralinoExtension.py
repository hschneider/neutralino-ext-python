# NeutralinoExtension
#
# A Python extension engine for Neutralino.
#
# Requirements:
# pypy -m pip install --no-binary :all: simple-websocket
# pypy -m pip install --no-binary :all: simple-websocket-server
#
# (c)2023-2024 Harald Schneider - marketmix.com

from argparse import *
import uuid, json, sys, os, signal
from queue import Queue
from threading import Thread
import websocket

class NeutralinoExtension:
    def __init__(self, debug=False):

        self.version = "1.2.5"

        self.debug = debug
        self.debugTermColors = True             # Use terminal colors
        self.debugTermColorIN = "\033[32m"      # Green: All incoming events, except function calls
        self.debugTermColorCALL = "\033[91m"    # Red: Incoming function calls
        self.debugTermColorOUT = "\033[33m"     # Yellow: Outgoing events

        if len(sys.argv) > 1:
            parser = ArgumentParser()
            parser.add_argument('--nl-port')
            parser.add_argument('--nl-token')
            parser.add_argument('--nl-extension-id')
            args = parser.parse_args()

            self.port = args.nl_port
            self.token = args.nl_token
            self.idExtension = args.nl_extension_id
            self.connectToken = ''
            self.urlSocket = f"ws://127.0.0.1:{self.port}?extensionId={self.idExtension}"
            self.callback = None
        else:
            conf = json.loads(sys.stdin.read())
            self.port = conf['nlPort']
            self.token = conf['nlToken']
            self.idExtension = conf['nlExtensionId']
            self.connectToken = conf['nlConnectToken']
            self.urlSocket = f"ws://127.0.0.1:{self.port}?extensionId={self.idExtension}&connectToken={self.connectToken}"

            self.debugLog('---')
            self.debugLog("Received extension config via stdin:")
            self.debugLog(json.dumps(conf, indent=4))
            self.debugLog('---')
            self.debugLog('WebSocket URL is:')
            self.debugLog(self.urlSocket)

        self.qSend = Queue()

        self.termOnWindowClose = True   # Terminate on windowCloseEvent message

        self.debugLog('---')
        self.debugLog(f"{self.idExtension} running on port {self.port}")
        self.debugLog('---')

    def sendMessage(self, event, data=None):
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

        self.debugLog(d, 'out')
        self.socket.send(json.dumps(d))

    def onOpen(self, ws):
        """
        WebSocket opened event.
        :param ws: WebSocket
        :return: -
        """
        self.debugLog("WebSocket_Event onOpen")

    def onMessage(self, ws, msg):
        """
        WebSocket message received event.
        This does some pre-processing before it delegates data to self.callback.
        :param ws: WebSocket
        :param msg: Message as string
        :return: -
        """

        self.debugLog(msg, 'in')
        d = json.loads(msg)

        if self.termOnWindowClose:
            if d['event'] == 'windowClose' or d['event'] == 'appClose':
                pid = os.getpid()
                os.kill(pid, signal.SIGTERM)
                return

        self.callback(d)

    def onError(self, ws, error):
        """
        WebSocket error event.
        :param ws: WebSocket
        :param error: Error
        :return: -
        """
        # Enable this to debug, but keep off in production mode:
        # self.debugLog(f"WebSocket_Event onError : {error}")
        pass

    def onClose(self, ws, close_status_code, close_msg):
        """
        WebSocket closed event.
        :param ws: WebSocket
        :param close_status_code: Status code
        :param close_msg: Status message
        :return: -
        """
        self.debugLog(f"WebSocket_Event onClose : StatusCode {close_status_code} {close_msg}")

    def run(self, onReceiveMessage):
        """
        Socket-handler main loop. Sends and receives messages.
        :param onReceiveMessage: Callback for incoming messages
        :return: --
        """

        self.callback = onReceiveMessage

        # Enable to debug:
        # websocket.enableTrace(True)

        self.socket = websocket.WebSocketApp(self.urlSocket,
                                    on_open=self.onOpen,
                                    on_message=self.onMessage,
                                    on_error=self.onError,
                                    on_close=self.onClose)

        # Enable auto-reconnect with reconnect=5 :
        self.socket.run_forever()

    def runThread(self, f, t, d):
        """
        Start a threaded background task.
        fn: Task function
        t: Task name
        d: Data to process
        """
        thread = Thread(target=f, name=t, args=(d,))
        thread.daemon = True
        thread.start()

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
            p = json.loads(p)
        except:
            pass

        return f, p

    def isEvent(self, e, eventName):
        """
        Check if e contains a particular event.
        :param e: Event data package as dict.
        :param eventName: Event name as string
        :return: Boolean
        """
        if 'event' in e and e['event'] == eventName:
            return True
        return False

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
