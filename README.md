<p align="center">
<img src="https://marketmix.com/git-assets/neutralino-ext-python/neutralino-python-header.svg" style="margin-left:auto;margin-right:auto">
</p>

# neutralino-ext-python
**A Python Extension for Neutralino**

This extension adds a Python3 backend to Neutralino with the following features:
- Requires only a few lines of code on both ends.
- Read all events from the Neutralino app in your Python code.
- Run Python functions from Neutralino.
- Run Neutralino functions from Python.
- All communication between Neutralino and Python runs asynchronously.
- All events are queued, so none will be missed during processing.
- Track the data flow between Neutralino and Python in realtime.
- Works in Window- and headless Cloud-Mode.
- Terminates the Python interpreter when the Neutralino app quits.

![Neutralino Python Extension](https://marketmix.com/git-assets/neutralino-ext-python/neutralino-python-extension.gif)

## Run the demo
The demo opens a Neutralino app. Clicking on the blue link sends a Ping to Python, which replies with Pong.
This illustrates the data-flow in both directions. 

Before running the demo, adapt the path to your Python interpreter in the **neutralino.config.json** file:

Replace this:
```json
 "extensions": [
    {
      "id": "extPython",
      "commandDarwin": "${NL_PATH}/extensions/python/_interpreter/python3.framework/Versions/Current/bin/python3 ${NL_PATH}/extensions/python/main.py",
      "commandWindows": "${NL_PATH}/extensions/python/_interpreter/pypy3/pypy.exe ${NL_PATH}/extensions/python/main.py"
    }
  ]
```
with e.g. 
```json
 "extensions": [
    {
      "id": "extPython",
      "commandDarwin": "python3 ${NL_PATH}/extensions/python/main.py",
      "commandWindows": "python3 ${NL_PATH}/extensions/python/main.py"
    }
  ]
```

When including the extension in your own project, make sure that your config contains this whitelist:
```json
  "nativeAllowList": [
    "app.*",
    "os.*",
    "window.*",
    "events.*",
    "extensions.*",
    "debug.log"
  ],
```

Next, prepare your Python environment with:
```commandline
# python3 -m pip install --no-binary :all: websocket-client
```

After this, run these commands in the ext-python folder:
```commandline
neu update
neu run
```

## Integrate into your own project
Just follow these steps:
- Modify **neutralino.config.json**, like mentioned in **"Run the demo"**.
- Copy the **extensions** folder to your project.
- Adapt the Python code in **extensions/python/main.py** to your needs.
- Copy **resources/js/python-extension.js** to **resources/js**.
- Add `<script src="js/python-extension.js"></script>` to your **index.html**
- Add `const PYTHON = new PythonExtension(true)` to your **main.js**
- Add **PYTHON.run(function_name, data) to main.js** to run Python functions from Neutralino.
- Add **event listeners to main.js**, to fetch result data from Python.

## ./extensions/python/main.py explained

```Python
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
        # f: function name, d: data as JSON or string
        #
        if f == 'ping':
            ping(d)


# Activate extension
#
ext = NeutralinoExtension(DEBUG)
ext.run(processAppEvent)
```

The extension is activated with the last 2 lines. 
**processAppEvent** is a callback function, which is triggered with each event coming from the Neutralino app.

In the callback function, you can process the incoming events by their name. In this case we react to the **"runPython"** event.
**parseFunctionCall(data)** extracts the **function name (f)** and its **parameters (p)** from the event's data package. Variable p can be a string or JSON dictionary.

if the requested function is named ping, we call the ping-function which sends a message back to Neutralino. 

**sendMessage()** requires the following parameters:
- An event name, here "pingResult"
- The data package to send, which can be of type string or JSON.

The **DEBUG** variable tells the NeutralinoExtension to report each event to the console. Incoming events, incoming function calls and outgoing messages are printed in different colors.
This makes debugging easier, since you can track the data flow between Neutralino and Python:

![Debug Python](https://marketmix.com/git-assets/neutralino-ext-python/debug-python.jpg)

## ./resources/js/main.js explained
```Javascript

async function onPingResult(e) {
 ...
}

// Init Neutralino
//
Neutralino.init();
...
Neutralino.events.on("pingResult", onPingResult);
...
// Init Python Extension
const PYTHON = new PythonExtension(true)
```

The last line initializes the JavaScript part of the Python extension. It's important to place this after Neutralino.init() and after all event handlers have been installed. Put it in the last line of your code and you are good to go. The const **PYTHON** is accessible globally and **must not be renamed.**

The **PythonExtension class** takes only 1 argument which instructs it to run in debug mode (here true). In this mode, all data from the Python extension is printed to the dev-console:

![Debug Meutralino](https://marketmix.com/git-assets/neutralino-ext-python/debug-neutralino.jpg)

The **pingResult event handler** listens to messages with the same name, sent by sendMessage() on Python's side. 

In **index.html**, you can see how to send data from Neutralino to Python, which is dead simple:
```html
<a href="#" onclick="PYTHON.run('ping', 'Neutralino says PING!');">Send PING to Python</a><br>
```

**PYTHON.run()** takes 2 arguments:
- The Python function to call, here "ping"
- The data package to submit, either as string or JSON.

Below this link, you see
```html
<a id="link-quit" href="#" onclick="PYTHON.stop();" style="display:none">Quit</a>
```
**PYTHON.stop()** is only required, when running Neutralino in cloud-mode. This will unload the Python extension gracefully.

## Classes overview

### NeutralinoExtension.py

NeutralinoExtension Class:

| Method                           | Description                                                  |
| -------------------------------- | ------------------------------------------------------------ |
| NeutralinoExtension(debug=false) | Extension class. debug: Print data flow to the terminal.     |
| debugLog(msg, tag="info")        | Write a message to the terminal.<br />msg: Message<br />tag: The message type, "in" for incoming, "out" for outgoing, "info" for others. |
| isEvent(d, e)                    | Checks if the incoming event data package contains a particular event.<br />d: Data-package<br />e: Event-name |
| parseFunctionCall(d)             | Extracts function-name (f) and parameter-data (p) from a message data package. Returns (f, p).<br />d: Data-package. |
| run(onReceiveMessage)            | Starts the sockethandler main loop. <br />onReceiveMessage: Callback function for incoming messages. |
| runThread(f, t, d):              | Starts a background task. <br />f: Task-function<br />t: Task-name<br />d: Data-package |
| sendMessage(e, d=None)           | Send a message to Neutralino. <br />e: Event-name,<br />d: Data-package as string or JSON dict. |

| Property    | Description                                               |
| ----------- | --------------------------------------------------------- |
| debug       | If true,  data flow is printed to the terminal            |
| pollSigStop | If true, then polling for long running tasks is inactive. |

### python-extension.js

PythonExtension Class:

| Method               | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| async run(f, p=null) | Call a Python function. f: Function-name, p: Parameter data package as string or JSON. |
| async stop()         | Stop and quit the Python extension and its parent app. Use this if Neutralino runs in Cloud-Mode. |

| Property | Description                                        |
| -------- | -------------------------------------------------- |
| debug    | If true,  data flow is printed to the dev-console. |

Events, sent from the frontend to the extension:

| Event    | Description                                                  |
| -------- | ------------------------------------------------------------ |
| appClose | Notifies the extension, that the app will close. This quits the extension. |

## More about Neutralino

- <u>[NeutralinoJS Home](https://neutralino.js.org)</u> 
- <u>[Neutralino Build Automation for macOS, Windows, Linux](https://github.com/hschneider/neutralino-build-scripts)</u>

- <u>[Neutralino related blog posts at marketmix.com](https://marketmix.com/de/tag/neutralinojs/)</u>



<img src="https://marketmix.com/git-assets/star-me-2.svg">
