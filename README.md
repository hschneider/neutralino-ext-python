# neutralino-ext-python
**A Python Extension for Neutralino**

This extension adds a Python3 backend to Neutralino with the following features:
- Read all events from the Neutralino app in your Python code.
- Run Python functions from Neutralino.
- Run Neutralino functions from Python.
- All communication between Neutralino and Python runs asynchronously.
- All events are queued, so none will be missed during processing.
- Track the data flow between Neutralino and Python in realtime.

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

After the config has been saved, run these commands in the ext-python folder:
```
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
- Add **event listeners to main.js**, to fetch data from Python.
- Add **PYTHON.run(function_name, data) to main.js** to submit data to Python.

## main.py explained

```Python
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

        # Process incoming method calls:
        # m: method name, d: data as JSON or string
        #
        if f == 'ping':
            ping(d)


# Activate extension
#
ext = NeutralinoExtension(DEBUG)
asyncio.run(ext.run(processAppEvent))
```

The extension is activated with the last 2 lines. 
**processAppEvent** is a callback function, which is triggered with each event coming from the Neutralino app.

In the callback function, you can process the incoming events by their name. In this case we react to the **"runPython"** event.
**parseFunctionCall** extracts the **function name (f)** and its **parameters (p)** from the event's data package. Variable p can be a string or JSON dictionary.

if the requested function is named ping, we call the ping-function which sends a message back to Neutralino. 

**sendMessage()** requires the following parameters:
- An event name, here "pingResult"
- The data package to send, which can be of type string or JSON.

The **DEBUG** variable tells the NeutralinoExtension to report each event to the console. Incoming events, incoming function calls and outgoing messages are printed in different colors.
This makes debugging easier, since you can track the data flow between Neutralino and Python:

![Debug Python](https://marketmix.com/git-assets/neutralino-ext-python/debug-python.jpg)

## main.js explained
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

The last line initializes the JavaScript part of the Python extension. It's important to place this after Neutralino.init() and after all event handlers have been installed. Put it in the last line of your code and you are good to go. The const **PYTHON** is accessible globally.

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

**PYTHON.stop()** is only required, when running Neutralino in cloud-mode. This will unload the Python extension gracefully.

## More about Neutralino
[Neutralino Home](https://neutralino.js.org) 

[Neutralino related blog posts at marketmix.com](https://marketmix.com/de/tag/neutralinojs/)

