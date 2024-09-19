const STATE_MEMORY = 0;
const STATE_SESSION = 1;
const STATE_COOKIE = 2;

class State {
    static MEMORY = STATE_MEMORY;
    static SESSION = STATE_SESSION;
    static COOKIE = STATE_COOKIE;

    constructor(appName, cookieExpDays=365) {
        this._var = {};
        this._sessions = new Set();
        sessionStorage.SessionName = appName;
        this._cookies = new Set();
        this._cookieExpDays = cookieExpDays;
        this._cb = {};
    }
    removeAll() {
        var keys = Object.keys(this._var);
        keys.forEach((key, index) => {
            this.remove(key);
        });
        var keys = Array.from(this._cookies);
        keys.forEach((key, index) => {
            this.remove(key);
        });
        var keys = Array.from(this._sessions);
        keys.forEach((key, index) => {
            this.remove(key);
        });
    }
    remove(name, removeCallbacks=false) {
        this._sessions.delete(name);
        this._cookies.delete(name);
        delete this._var[name];  
        sessionStorage.removeItem(name);
        this.deleteCookie(name);
        for (const cb of this.getCBs(name)) {
            cb();
        }
        if (removeCallbacks) {
            this.removeAllCBs(name);
        }
    }
    async set(name, value, persist=0) { // 0: memory, 1: session, 2: cookie
        var prev = this.get(name);
        if (persist === 0) {
            this._var[name] = value;            
            this._sessions.delete(name);
            this._cookies.delete(name);
            sessionStorage.removeItem(name);
            this.deleteCookie(name);
        }
        else if (persist === STATE_SESSION) {
            delete this._var[name];
            this._sessions.add(name);
            this._cookies.delete(name);
            sessionStorage.setItem(name, value);            
            this.deleteCookie(name);
        } else if (persist === STATE_COOKIE) {
            delete this._var[name];
            this._sessions.delete(name);
            this._cookies.add(name);
            sessionStorage.removeItem(name, value);            
            this.setCookie(name, value);
        }
        if (prev != value) {
            for (const cb of this.getCBs(name)) {
                cb(value);
            }
        }
        return this.get(name);
    }
    get(name, fallback=null) {
        if (this._var[name] != null) return this._var[name];

        // session and cookies are stored in strings
        let value = null;
        if (sessionStorage.getItem(name) != null) {
            value = sessionStorage.getItem(name);
        } else if (this.getCookie(name) != null) {
            value = this.getCookie(name);
        }
        if (value != null) {
            if (value === 'null') {
                value = null;
            } else if (value === 'true') {
                value = true;
            } else if (value === 'false') {
                value = false;
            // need this check as JS converts to number as long as the fist character is numeric (e.g. '1$#' converts to 1)
            } else if (/^\d+$/.test(value)) {
                value = parseFloat(value);
            }
            return value;
        }
        return fallback;
    }
    getCBs(name) {
        if (this._cb[name] == undefined) {
            this._cb[name] = new Array();
        }
        return this._cb[name];
    }
    addCB(name, fn) {
        var cbs = this.getCBs(name);
        cbs.push(fn);
    }
    removeCB(name, fn) {
        var cbs = this.getCBs(name);
        for (var i = 0; i < cbs.length; i++) {
            if (cbs[i] === fn) {
                cbs.splice(i, 1);
                break;
            }
        }
    }
    removeAllCBs(name) {
        delete this._cb[name];
    }
    setCookie(name, value, days=365) {
        var expires = '';
        var encoded = encodeURIComponent(value);
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days*24*60*60*1000));
            expires = '; expires=' + date.toUTCString();
        }
        document.cookie = name + "=" + (encoded || "")  + expires + "; path=/";
    }
    getCookie(name) {
        var nameEQ = name + '=';
        var ca = document.cookie.split(';');
        for(var i=0;i < ca.length;i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) == 0) {
                var value = decodeURIComponent(c.substring(nameEQ.length,c.length));
                return value;
            }
        }
        return null;
    }
    deleteCookie(name) {   
        document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }
}
