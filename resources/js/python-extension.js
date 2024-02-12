// PythonExtension
//
// Run PythonExtension functions by sending dispatched event messages.
//
// (c)2023-2024 Harald Schneider - marketmix.com

class PythonExtension {
    constructor(debug=false) {
        this.version = '1.1.2';
        this.debug = debug;

        this.pollSigStop = true;
        this.pollID = 0;

        // Init callback handlers for polling.
        //
        Neutralino.events.on("startPolling", this.onStartPolling);
        Neutralino.events.on("stopPolling", this.onStopPolling);
    }
    async run(f, p=null) {
        //
        // Call a PythonExtension function.

        let ext = 'extPython';
        let event = 'runPython';

        let data = {
            function: f,
            parameter: p
        }

        if(this.debug) {
            console.log(`EXT_PYTHON: Calling ${ext}.${event} : ` + JSON.stringify(data));
        }

        await Neutralino.extensions.dispatch(ext, event, data);
    }

    async stop() {
        //
        // Stop and quit the Python extension and its parent app.
        // Use this if Neutralino runs in Cloud-Mode.

        let ext = 'extPython';
        let event = 'appClose';

        if(this.debug) {
            console.log(`EXT_PYTHON: Calling ${ext}.${event}`);
        }
        await Neutralino.extensions.dispatch(ext, event, "");
        await Neutralino.app.exit();
    }

    async onStartPolling(e)  {
        //
        // This starts polling long-running tasks.
        // Since this is called back from global context,
        // we have to refer 'RUST' instead of 'this'.

        PYTHON.pollSigStop = false
        PYTHON.pollID = setInterval(() => {
            if(PYTHON.debug) {
                console.log("EXT_RUST: Polling ...")
            }
            PYTHON.run("poll")
            if(PYTHON.pollSigStop) {
                clearInterval(PYTHON.pollID);
            };
        }, 500);
    }

    async onStopPolling(e)  {
        //
        // Stops polling.
        // Since this is called back from global context,
        // we have to refer 'RUST' instead of 'this'.

        PYTHON.pollSigStop = true;
        if(PYTHON.debug) {
            console.log("EXT_RUST: Polling stopped!")
        }
    }
}