# main.py 1.0.2
#
# Neutralino PythonExtension.
#
# (c)2023 Harald Schneider - marketmix.com

from NeutralinoExtension import *

DEBUG = True    # Print incoming event messages to the console

def ping(d):
    #
    # Send some data to the Neutralino app

    ext.sendMessage('pingResult', f'Python says PONG, in reply to "{d}"')

def processAppEvent(d):
    """
    Handle Neutralino app events.
    :param d: data package as JSON dict.
    :return: ---
    """

    if ext.isEvent(d, 'runPython'):
        (f, d) = ext.parseFunctionCall(d)

        # Process incoming function calls:
        # f: function-name, d: data as JSON or string
        #
        if f == 'ping':
            ping(d)


# Activate extension
#
ext = NeutralinoExtension(DEBUG)
asyncio.run(ext.run(processAppEvent))
