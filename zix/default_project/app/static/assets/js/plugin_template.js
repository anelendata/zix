// Rename MyPlugin in the class name, constant namespace, and the line at the bottom.
// Load this file before app.js in the html file and activate the line at the bottom.
let MyPlugin = (function() {
    const namespace = 'MyPlugin';
    let _setStateCallBacks = function() {
        let stateCBRegistry = [
            // name, callback=null
            ['me', _onMeChange],
        ];

        stateCBRegistry.forEach(o=>{
            App.getState().addCB(o[0], o[1]);
        });
    };

    // private properties

    // private methods
    let _initView = function() {
    };

    let _setUICallbacks = function() {
    };

    let _onMeChange = function(me) {
    };

    // Exposing private members
    return {
        name: namespace,
        // init will be called by App.init() if the plugin is registered (See the bottom of this file)
        init: function() {
            _initView();
            _setStateCallBacks();
            _setUICallbacks();
        },
    };
})();
// App.plugins.push(MyPlugin);
