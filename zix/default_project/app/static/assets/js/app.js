let App = $.fn.App = (function() {
    let _setStateCallBacks = function() {
        let stateCBRegistry = [
            // name, callback=null
            ['me', _onMeChange],
            ['account_uid', _onAccountUidChange],
        ];

        stateCBRegistry.forEach(o=>{
            state.addCB(o[0], o[1]);
        });
    };

    // private properties
    let state = null;

    let _login = function() {
        let hash = window.top.location.hash === null ? '' : window.top.location.hash;
        let url = '/login?next=' + window.location.pathname + hash;
        window.location = url;
    };

    let _logout = function(redirect=true) {
        state.remove('token');
        state.removeAll();
        if (redirect) {
            window.location = '/logout?federated';
        }
    };

    let _fetchNotifications = function() {
        if (!state.get('notifications')) {
            let default_ = {
                last_check: 0,
                latest: 1,
                notifications: [
                    {
                        'created_at': moment().unix(),
                        'message': 'No news is a good news :)',
                    },
                ],
            };
            state.set('notifications', JSON.stringify(default_), STATE_COOKIE);
        }
        let notif = JSON.parse(state.get('notifications'));
        get(Config.ApiPath + '/users/me/notifications').then(function(response) {
            notif.notifications = response;
            notif.latest = null;
            notif.notifications.forEach((obj) => {
                var createdAt = moment(moment(obj.created_at).format('YYYY-MM-DD HH:mm:ss.SSS') + 'Z').unix();
                if (!notif.latest || notif.latest < createdAt) {
                    notif.latest = createdAt;
                }
            });
            state.set('notifications', JSON.stringify(notif), STATE_COOKIE);
        }, function(error) {
        });
    };

    let _updateProfile = function(cb=null) {
        let token = state.get('token');
        if (!token) {
            state.set('loginStatus', {status: 'logout'});
            return;
        }
        state.set('lastTokenCheck', moment().utc().unix());
        let headers = [
            ['accept', 'application/json', false],
            ['Authorization', 'Bearer ' + token, false]
        ];
        let params = [];
        if (state.get('psid')) {
            params.push(['psid', state.get('psid')])
        }
        get(Config.ApiPath + '/users/me/', params, headers).then(response=>{
            state.set("me", response);
            state.remove('psid');
            if (cb) {
                cb();
            }
        }, error=>{
            AppView.showAlert('Oops, something went wrong. Please try again.', 'danger');
            state.remove('token');
        });
        // also fetch notificaitons
        _fetchNotifications();
    };

    let _setActiveAccountUID = function(accountUID, forceCB = false) {
        if (forceCB) {
            App.getState().set('active_account_uid', null, STATE_SESSION);
        }
        App.getState().set('active_account_uid', accountUID, STATE_SESSION);
    };

    let _setTokenAndPSIDFromHTML = function() {
        let access_token;
        let psid;
        if ($('#_data')[0]) {
            access_token = $('#_data')[0].dataset.token;    
            if (access_token) {
                state.set('token', access_token, persist=STATE_COOKIE);
            }
            psid = $('#_data')[0].dataset.psid;
            if (psid) {
                // keep this until the info is updated on server successfully
                state.set('psid', psid, persist=STATE_COOKIE);
            }
        }
    };

    let _checkLoginAlert = function() {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        if (urlParams.has('message')) {
            let loginStatus = {
                message: urlParams.get('message'),
                status: urlParams.get('success'),
            };
            state.set('loginStatus', loginStatus);
        }
    };

    let _onMeChange = function(me) {
        if (!me) {
            return;
        }
        if (me.account.uid) {
            state.set('account_uid', me.account.uid);
        }
    };

    let _onAccountUidChange = function(accountUID) {
        if (!accountUID) return;
        get(Config.ApiPath + '/users/me/settings').then(
            response=>{
                state.set('account_settings', response); 
            },
            error => {
            }
        );
    }; 

    // init() should be called first after everything is loaded.
    let _init = function() {
        state = new State(Config.Namespace);
        Config.ApiPath = Config.apiPath;
        App.plugins.forEach(plugin=>{
            console.info('Plugin ' + plugin.name + ' has been initialized');
            plugin.init(state);
        });

        // It should set the callbacks before any state changes.
        _setStateCallBacks();

        // most important business first
        _setTokenAndPSIDFromHTML();

        _checkLoginAlert();

        _updateProfile();
    };

    // Exposing private members
    return {
        init: _init,
        login: _login,
        logout: _logout,
        getState: function() {
            return state;
        },
        updateProfile: function(cb) {
            return _updateProfile(cb);
        },
        plugins: new Array(),
    };
})();

let AppView = $.fn.AppView = (function() {
    let Pages = null;

    let _setStateCallBacks = function() {
        let stateCBRegistry = [
            // name, callback=null
            ['loginStatus', _onLoginStatusChange],
            ['token', _onTokenChange],
            ['me', _onMeChange],
            ['notifications', _onNotificationChange],
        ];

        stateCBRegistry.forEach(o=>{
            state.addCB(o[0], o[1]);
        });
    };

    // private properties
    let state = null;

    let _resetView = function() {
        _showModal('#login-modal');
        $('.internal-release').hide();
        $('.btn-login-required').prop('disabled', true);

        if (isMobile()) {
            $('#mobile-sidebar-button').show();
        } else {
            $('#mobile-sidebar-button').hide();        
        }
        $('.support-email').text(Config.supportEmail);
    };

    let _setSidebar = function() {
        /*
        $('#sidebar').html(
            `<li class="nav-item logo-holder"><a id="sidebarToggleHolder" class="nav-link float-right" href="#"><span id="sidebarToggle">` + Icons.hamburgerMenu +
            `</a></span><div class="text-center text-white mx-4 py-4 logo"></div></li>`);
        */
        Object.keys(Pages).forEach(k=>{
            let icon = Pages[k].menuIcon || Icons.edit;
            let display = Pages[k].menuDisplay;
            $('#sidebar').append(`<li class="nav-item mx-3"><a id="sidebar-` + k + `" class="nav-link active text-left px-0 py-1" href="#` + k + `">` + icon + `<span class="text-nowrap mx-2">` + display + `</span></a></li>`);
            $('#sidebar-' + k).on('click', function(){_goToPage(k)});
        });
    };

    let _setUICallBacks = function() {
        $('#auth0-login-button').on('click', App.login);
        $('#auth0-logout-button').on('click', App.logout);
        $('#message-modal-button').on('click', function() {
            _hideModal('#message-modal');
        });
    };

    let _loadPages = function() {
        const tab = window.location.hash.substr(1);
        let index = 0;
        Object.keys(Pages).forEach(k=>{
            let page = Pages[k];
            if (!page.content && page.contentURL) {
                get(page.contentURL).then(response=>{
                    Pages[k].content = response.content;
                    $('#' + k).remove();
                    $('#content').append('<div id="' + k + '" style="display: none;">' + Pages[k].content + '</div>');
                    if (k && tab == k || (index == 0)) {
                        _goToPage(tab);
                    }
                }, error=>{
                    AppView.showAlert('Oops, something went wrong. Please try again.', 'danger');
                });
            }
            index++;
        });
    };

    let _init = function(appState) {
        state = appState;
        Pages = Config.pages;
        _resetView();
        _setSidebar();
        _setStateCallBacks();
        _setUICallBacks();
        _loadPages(); 
    };

    let _getCurrentPageName = function(h) {
        let end = h.search('__');
        if (end < 0) {
            end = h.length;
        }
        return h.substring(0, end);
    };

    let _goToPage = function(h) {
        let currentPage = _getCurrentPageName(h);
        let keys = Object.keys(Pages);
        if (!keys.includes(currentPage)) {
            currentPage = keys[0];
        }
        Object.keys(Pages).forEach(function(s, index){
            if (s == currentPage) {
                $('#' + s).show();
            } else {
                $('#' + s).hide();
            }
        });

        if (Pages[currentPage].function != undefined) {
            Pages[currentPage].function();
        }
        var url = location.href;
        location.href = "#" + currentPage;
        history.replaceState(null, null, url);

        if (isMobile()) {
            collapseSidebar();
        }
    };

    let _showAlert = function(alertText, style='danger', elemID='#alert', dismissable=true, disappearSeconds=10) {
        var css = '';
        if (disappearSeconds > 0) {
            css = 'style="-webkit-animation: cssAnimation ' + disappearSeconds + 's forwards; animation: cssAnimation ' + disappearSeconds + 's forwards;"';
        }
        if (dismissable) {
            $(elemID)[0].innerHTML = '<div role="alert" class="alert alert-' + style + ' alert-dismissible" ' + css +'><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button><span id="alert-text">' + alertText + '</span></div>';    
        } else {
            $(elemID)[0].innerHTML = '<div class="alert alert-' + style + '" role="alert" ' + css + '><span>' + alertText + '</span></div>';
        }
        if (disappearSeconds > 0) {
            // CSS does not remove the element and cause other UI elements blocked
            setTimeout((elemId) => {
                let alertElem = $(elemId);
                if (alertElem) {
                    alertElem.innerHTML = '';
                }
            }, (disappearSeconds + 1.0) * 1000, elemID);
        }
    };

    let _showModal = function(modalID, config=null) {
        if (!config) {
            config = {
                backdrop: 'static',
                keyboard: false
            }
        }
        $(modalID).data('bs.modal', null);
        $(modalID).modal(config, 'show');
    };

    let _hideModal = function(modalID) {
      $(modalID).modal('hide');
    };

    let _showNotifications = function() {
        let notif = state.get('notifications');
        if (!notif) return;
        notif = JSON.parse(notif);
        let message = '<ul>';
        notif.notifications.forEach((obj) => {
            message += '<li>' + moment(moment(obj.created_at).format('YYYY-MM-DD HH:mm:ss.SSS') + 'Z').format('YYYY-MM-DD') + ': ' + obj.message + '</li>';
        });
        message += '</ul>';
        showMessageModal(null, 'What\'s New', message, 'OK', onClose=null);
        notif.last_check = moment().utc().unix();
        state.set('notifications', JSON.stringify(notif), STATE_COOKIE);
    };

    let _handleHttpError = function(error) {
        let err = error;
        if (typeof error === 'string') {
            try {
                err = JSON.parse(error);
            } catch (e) {
                err = error;
            }
        }
        if (err.status == 401) {
            App.logout();
        } else {
            let msg = '';
            if (err.detail) msg = err.detail;
            if (err.response) {
                if (typeof err.response === 'string') {
                    try {
                        msg = JSON.parse(err.response);
                    } catch (e) {
                        msg = err.response;
                    }
                    if (msg.detail) {
                        msg = msg.detail;
                    }
                } else {
                    msg = err.response.toString();
                }
            }
            _showAlert(msg);
        }
    };

    let _updateAccountProfileDisplay = function(account) {
        if (!account) {
            return;
        }
        let firstName = account.first_name || 'User';
        let lastName = account.last_name || account.uid.slice(0, 8);
        $('.active-account-name').text(account.name);
        let profile_pic_url = account.profile_picture_url || 'https://gravatar.com/avatar/notset';
        $('.active-account-profile-image').attr('src', profile_pic_url);
        $('.active-account-full-name').text(firstName + ' ' + lastName);
    };
    let _onLoginStatusChange = function(value) {
        $('#auth0-login-check-img').hide();
        $('#auth0-login-button').show();
        $('#auth0-login-button').show();
        $('#auth0-logout-button').hide();
        if (!value || value.status === 'logout') return;
        if (value.status === 'true') {
            _showAlert(value.message, 'success', '#login-alert');
        } else {
            _showAlert(value.message, 'danger', '#login-alert', false, -1);
            $('#auth0-login-button').hide();
            $('#auth0-logout-button').show();
        }
    };

    let _onTokenChange = function(value) {
        if (!value || value === 'expired') {
            _showModal('#login-modal');
        } else {
            _hideModal('#login-modal');
        }
    };

    let _onMeChange = function(me) {
        if (!me) {
            // btn-login-required is used for disabling certain buttons for demo page
            $('.btn-login-required').prop("disabled",true);
            $('#auth0-login-check-img').hide();
            $('#auth0-login-button').show();
            $('#auth0-logout-button').hide();
            _showModal('#login-modal');
            return;
        }

        $('.btn-login-required').removeAttr("disabled"); 
        _updateAccountProfileDisplay(me.account);
        $('.hide-after-login').hide();
        setTimeout(function(){_hideModal('#login-modal')}, 500);

        if (me.is_staff) {
            $('#admin-mode-nav-item').show();
        } else {
            $('#admin-mode-nav-item').hide();
        }

        let dropDownHtml = '<a id="notifications" class="dropdown-item" href="#" onclick="App.View.showNotifications()">Notifications<div class="notification-alert">' + Icons.circleFill + '</div></a>';

        if (me.is_staff) {
            dropDownHtml += '<a id="admin-mode-nav-item" class="dropdown-item" href="#"><span id="admin-switch">' + Icons.toggleOff + '</span><span class="text-nowrap mx-2">Admin</span></a>';
        }

        dropDownHtml += '<a class="dropdown-item" href="#" onclick="App.logout()"><img src="https://gravatar.com/avatar/hello" class="profile-image-tiny" /> Logout</a>';
        $('#user-menu').html(dropDownHtml);
        $('.notification-alert').hide();

        if (me.is_staff) {
            $('#admin-mode-nav-item').on('click', function() {
                if (state.get('admin-mode') === 'on') {
                    state.set('admin-mode', 'off');
                    $('#admin-switch').html(Icons.toggleOff);
                    $('.internal-release').hide();
                } else {
                    state.set('admin-mode', 'on');
                    $('#admin-switch').html(Icons.toggleOn);
                    $('.internal-release').show();
                }
            });
        }

        let name = me.account.name || ('User ' + me.account.uid.slice(0, 8));
        // Update accounts pulldown
        let acctDropdownHtml = '<a class="dropdown-item" href="#"><strong>Personal</strong></a><a class="dropdown-item" href="#" onclick="App.setActiveAccountUID(\'' + me.account.uid + '\')">' + name + '</a>';
        acctDropdownHtml += '<div class=dropdown-divider></div><a class="dropdown-item" href="#"><strong>Company</strong></a>';

        let validActiveAccount = me.account.uid;
        let memberships = me.memberships || [];
        memberships.forEach(function(obj, index) {
            let organization_name = obj.name || ('Organization ' + obj.uid.slice(0, 8));
            if (obj.status != 'active') {
                return;
            }
            acctDropdownHtml += '<a class="dropdown-item" href="#" onclick="App.setActiveAccountUID(\'' + obj.account.uid + '\')">&nbsp;' + organization_name + '</a>';

            if (state.get('active_account_uid') == obj.account.uid) {
                validActiveAccount = obj.account.uid;
            }
        });
        acctDropdownHtml += '<div class=dropdown-divider></div><a class="dropdown-item" href="#" onclick="OCOrganization.showNewOrgModal()">&nbsp;Create...</a>';
        $('#accounts').html(acctDropdownHtml);
    };

    let _onNotificationChange = function(value) {
        if (!value) {
            $('.notification-alert').hide();
            return;
        }
        let notifications = JSON.parse(value);
        if (notifications == null) return;
        let lastCheck = notifications.last_check;
        let latest = notifications.latest;
        if (latest <= lastCheck) {
            $('.notification-alert').hide();
        } else {
            $('.notification-alert').show();
        }
    };

    return {
        name: 'AppView',
        init: _init,
        tabs: Pages,
        showAlert: _showAlert,
        goToPage: _goToPage,
        handleHttpError: _handleHttpError,
        getCurrentPageName: _getCurrentPageName,
    };
})();
App.plugins.push(AppView);

$(document).ready(function(){
    App.init();
});
