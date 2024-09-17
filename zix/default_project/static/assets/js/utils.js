function roundUnixTimestamp(unixTimestamp, min) {
    return Math.floor(unixTimestamp / 1000 / 60 / min) * 1000 * 60 * min;
}

function moveByMinutes(ts, minutes=30) {
    // Return the time of nearest YYYY-MM-DD XX:00/15/30:00.000 etc forward or backward
    var base = minutes;
    if (minutes < 0) {
        base = 0;
    }
    var residual = base - (ts.seconds(0).milliseconds(0).minute() % Math.abs(minutes));
    return moment(ts.seconds(0).milliseconds(0)).add(residual, 'minutes');
}

function truncateByWords(str, num_words) {
    return str.split(" ").splice(0, num_words).join(" ");
}

function toSingleSpace(text) {
    const regex = /[.,;?!-][.,;?!-]*/g;
    return text.replaceAll('\n', ' ').replace(regex, ' ').replace(/[ ][ ]*/g, ' ').trim();
}

function countWords(text) {
    var singleSpace = toSingleSpace(text);
    var wc = singleSpace == '' ? 0 : singleSpace.split(' ').length;
    return wc;
}

function getBrowser() {
    // https://stackoverflow.com/a/9851769
    // Opera 8.0+
    var isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;

    // Firefox 1.0+
    var isFirefox = typeof InstallTrigger !== 'undefined';

    // Safari 3.0+ "[object HTMLElementConstructor]" 
    var isSafari = /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && window['safari'].pushNotification));

    // Internet Explorer 6-11
    var isIE = /*@cc_on!@*/false || !!document.documentMode;

    // Edge 20+
    var isEdge = !isIE && !!window.StyleMedia;

    // Chrome 1 - 79
    var isChrome = !!window.chrome && (!!window.chrome.webstore || !!window.chrome.runtime);

    // Edge (based on chromium) detection
    var isEdgeChromium = isChrome && (navigator.userAgent.indexOf("Edg") != -1);

    // Blink engine detection
    var isBlink = (isChrome || isOpera) && !!window.CSS;
}

function insertAtCursor(myField, myValue) {
    //IE support
    if (document.selection) {
        myField.focus();
        sel = document.selection.createRange();
        sel.text = myValue;
    }
    //MOZILLA and others
    else if (myField.selectionStart || myField.selectionStart == '0') {
        var startPos = myField.selectionStart;
        var endPos = myField.selectionEnd;
        myField.value = myField.value.substring(0, startPos)
            + myValue
            + myField.value.substring(endPos, myField.value.length);
    } else {
        myField.value += myValue;
    }
}

function copyText(target) {
    var text = $(target).html().replaceAll('<br>', '\n').replaceAll('&nbsp;', ' ').replaceAll('<br/>', '\n').replace( /(<([^>]+)>)/ig, '');
    navigator.clipboard.writeText(text);
}

function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

function _typeWriter(target, text, isHtml, pos, speed) {
    if (pos < text.length) {
        var html = $(target).html();
        var c = text.charAt(pos);
        if (isHtml) {
            switch (c) {
                case '\n':
                    c = '<br>';
                    break;
                case ' ':
                    c = '&nbsp;';
                    break;
            }
        }
        $(target).html(html + c);
        pos++;
        setTimeout(_typeWriter, speed, target, text, isHtml, pos, speed);
    }
}

async function typeWriter(target, text, isHtml=false, speed=25) {
    _typeWriter(target, text, isHtml, 0, speed);
}
