// PythonExtension
//
// Run PythonExtension functions by sending dispatched event messages.
//
// (c)2023-2024 Harald Schneider - marketmix.com

class PythonExtension {
    constructor(debug=false) {
        this.version = '1.1.4';
        this.debug = debug;

        if(NL_MODE !== 'window') {
            window.addEventListener('beforeunload', function (e) {
                e.preventDefault();
                e.returnValue = '';
                PYTHON.stop();
                return '';
            });
        }
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