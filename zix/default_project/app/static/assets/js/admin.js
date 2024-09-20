let Admin = (function() {
    const namespace = 'Admin';
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
    let UsersTable = null;
    var UsersList = null;

    // private methods
    let _initView = function() {
    };

    let _setUICallbacks = function() {
    };

    let _onMeChange = function(me) {
        _fetchUsers();
    };

    let _updateTable = function(target, table, data, colFields=null, searchField=null) {
        if (!colFields) {
            colFields = {};
            Object.keys(data[0]).forEach(k=>{
                colFields[k] = k;
            });
        }
        if (table == null) {
            var rows = 5;
            if (isMobile()){
                rows = 3;
                delete colFields.createdAtDisplay;
            }
            // https://table-sortable.vercel.app/story-latest.html
            table = $(target).tableSortable({
                data: data,
                columns: colFields,
                rowsPerPage: rows,
                pagination: true,
                searchField: searchField,
                sortingIcons: {
                    asc: '<span>▲</span>',
                    desc: '<span>▼</span>',
                }            
            });
        } else {
            table.setData(
                data,
                colFields,
                false,
            );
        }
        return table;
    };

    var _fetchUsers = function() {
        let path = '/admin/users';
        get(ApiPath + path, []).then(users => {
            UsersList = [];
            users.forEach(u=>{
                let record = {};
                Object.keys(u).forEach(k=>{
                    let v = u[k];
                    if (k === 'uid') {
                        v = v.slice(0, 8);
                    }
                    if (typeof(v) === 'object') {
                        v = v.uid.slice(0, 8) || 'object';
                    }
                    record[k] = v;
                });
                UsersList.push(record);
            });
            UsersTable = _updateTable(
                '#users-table',
                UsersTable,
                UsersList,
                null,
                '#search-input'
            );
        }, error => {
            if (error) {
                logout();
            }
        });
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
// Load this file before app.js and activate the next line
App.plugins.push(Admin);
