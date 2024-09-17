const ApiPath = '/api/v1';
const Namespace = 'ZixCore';
const supportEmail = 'support@anelen.co';

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
            state.set('notifications', JSON.stringify(default_), State.COOKIE);
        }
        let notif = JSON.parse(state.get('notifications'));
        get(App.ApiPath + '/users/me/notifications').then(function(response) {
            notif.notifications = response;
            notif.latest = null;
            notif.notifications.forEach((obj) => {
                var createdAt = moment(moment(obj.created_at).format('YYYY-MM-DD HH:mm:ss.SSS') + 'Z').unix();
                if (!notif.latest || notif.latest < createdAt) {
                    notif.latest = createdAt;
                }
            });
            state.set('notifications', JSON.stringify(notif), State.COOKIE);
        }, function(error) {
        });
    };

    let _updateProfile = function(cb=null) {
        token = state.get('token');
        if (!token) {
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
        get(ApiPath + '/users/me/', params, headers).then(response=>{
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
                state.set('token', access_token, persist=State.COOKIE);
            }
            psid = $('#_data')[0].dataset.psid;
            if (psid) {
                // keep this until the info is updated on server successfully
                state.set('psid', psid, persist=State.COOKIE);
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
        get(ApiPath + '/users/me/settings').then(
            response=>{
                state.set('account_settings', response); 
            },
            error => {
            }
        );
    };

    // init() should be called first after everything is loaded.
    let _init = function() {
        state = new State(Namespace);
        AppView.init(state);

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
        ApiPath: ApiPath,
    };
})();

let AppView = $.fn.AppView = (function() {
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

    let Tabs = {
        'tab-1': undefined,
        settings: undefined,
        help: undefined,
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
        $('.support-email').text(supportEmail);
    };

    let _setSidebar = function() {
        Object.keys(Tabs).forEach(k=>{
            $('#sidebar-' + k).on('click', function(){_goToTab(k)});
        });
    };

    let _setUICallBacks = function() {
        $('#auth0-login-button').on('click', App.login);
        $('#auth0-logout-button').on('click', App.logout);
        $('#message-modal-button').on('click', function() {
            _hideModal('#message-modal');
        });
    };

    let _init = function(appState) {
        state = appState;
        _resetView();
        _setSidebar();
        _setStateCallBacks();
        _setUICallBacks();
        let tab = window.location.hash.substr(1);
        _goToTab(tab);
    };

    let getCurrentTabName = function(h) {
        end = h.search('__');
        if (end < 0) {
            end = h.length;
        }
        return h.substring(0, end);
    };

    let _goToTab = function(h) {
        let me = state.get('me');
        let currentTab = getCurrentTabName(h);
        let keys = Object.keys(Tabs);
        if (!keys.includes(currentTab)) {
            currentTab = keys[0];
        }
        Object.keys(Tabs).forEach(function(s, index){
            if (s == currentTab) {
                $('#' + s).show();
            } else {
                $('#' + s).hide();
            }
        });

        if (Tabs[currentTab] != undefined) {
            Tabs[currentTab]();
        }
        var url = location.href;
        location.href = "#" + currentTab;
        history.replaceState(null, null, url);

        if (isMobile()) {
            collapseSidebar();
        }
    };

    let _showAlert = function(alertText, style='danger', elemID='alert', dismissable=true, disappearSeconds=10) {
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
        $('#auth0-login-button').show();
        $('#auth0-logout-button').hide();
        if (!value) return;
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
            _showModal('#login-modal');
            return;
        }

        _updateAccountProfileDisplay(me.account);
        $('.hide-after-login').hide();
        setTimeout(function(){_hideModal('#login-modal')}, 500);

        if (me.is_staff) {
            $('#admin-mode-nav-item').show();
        } else {
            $('#admin-mode-nav-item').hide();
        }

        let dropDownHtml = '<a id="notifications" class="dropdown-item" href="#" onclick="App.View.showNotifications()">Notifications<div class="notification-alert">' + circleFillIcon + '</div></a>';
        if (me.isstateaff) {
            dropDownHtml += '<a id="admin-mode-nav-item" class="dropdown-item" href="#"><span id="admin-switch">' + toggleOffIcon + '</span><span class="text-nowrap mx-2">Admin</span></a>';
        }
        dropDownHtml += '<a class="dropdown-item" href="#" onclick="App.logout()"><img src="https://gravatar.com/avatar/hello" class="profile-image-tiny" /> Logout</a>';
        $('#user-menu').html(dropDownHtml);
        $('.notification-alert').hide();

        if (me.isstateaff) {
            $('#admin-mode-nav-item').on('click', function() {
                if (state.get('admin-mode') === 'on') {
                    state.set('admin-mode', 'off');
                    $('#admin-switch').html(toggleOffIcon);
                    $('.internal-release').hide();
                } else {
                    state.set('admin-mode', 'on');
                    $('#admin-switch').html(toggleOnIcon);
                    $('.internal-release').show();
                }
            });
        }

        let name = me.account.name || ('User ' + me.account.uid.slice(0, 8));
        // Update accounts pulldown
        let acctDropdownHtml = '<a class="dropdown-item" href="#"><strong>Personal</strong></a><a class="dropdown-item" href="#" onclick="App.setActiveAccountUID(\'' + me.account.uid + '\')">' + name + '</a>';
        acctDropdownHtml += '<div class=dropdown-divider></div><a class="dropdown-item" href="#"><strong>Company</strong></a>';

        let validActiveAccount = me.account.uid;
        memberships = me.memberships || [];
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
        init: _init,
        showAlert: _showAlert,
        goToTab: _goToTab,
        showNotifications: _showNotifications,
    };
})();



$(document).ready(function(){
    App.init();
});
