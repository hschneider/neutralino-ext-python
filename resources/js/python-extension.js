// PythonExtension
//
// Run PythonExtension functions by sending dispatched event messages.
//
// (c)2023 Harald Schneider

class PythonExtension {
    constructor(debug=false) {
        this.version = '1.1.0';
        this.debug = debug;
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
}