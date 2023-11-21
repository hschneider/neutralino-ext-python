# main.py 1.0.1
#
# Neutralino PythonExtension.
#
# (c)2023 Harald Schneider

from NeutralinoExtension import *

DEBUG = True    # Print incoming event messages to the console

def ping(d):
    #
    # Send some data to the Neutralino app

    ext.sendMessage('pingResult', f'Python says PONG, in reply to "{d}"')

def processAppEvent(data):
    """
    Handle Neutralino app events.
    :param data: data package as JSON dict.
    :return: ---
    """

    if data['event'] == 'runPython':
        (f, d) = ext.parseFunctionCall(data)

        # Process incoming function calls:
        # f: function-name, d: data as JSON or string
        #
        if f == 'ping':
            ping(d)


# Activate extension
#
ext = NeutralinoExtension(DEBUG)
asyncio.run(ext.run(processAppEvent))
