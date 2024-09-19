/* UI */
function blur(elemID) {
    $('#' + elemID).css('filter', 'blur(5px)');
}

function unblur(elemID) {
    $('#' + elemID).css('filter', 'blur(0px)');
}

function enable(path) {
    $(path).removeClass('disabled');
    $(path).prop('disabled', false);
}

function disable(path) {
    $(path).prop('disabled', true);
}

var confetti;
function shootConfetti(targetID, params) {
    // https://github.com/loonywizard/js-confetti
    confetti = new JSConfetti($('#message-modal'));
    confetti.addConfetti(params).then(() => function(){confetti.clearCanvas()});
    return confetti;
}

function hideModal(modalID) {
  $('#' + modalID).modal('hide');
}

function showModal(modalID, config=null) {
    if (!config) {
        config = {
            backdrop: 'static',
            keyboard: false
        }
    }
    $('#' + modalID).data('bs.modal', null);
    $('#' + modalID).modal(config, 'show');
}

function showThemedModal(modalID, theme, headline=null, body=null, config=null) {
    configs = {
        celebration: {
            emojis: ['🌈', '⚡️', '🦄', '✨', '💫', '🌸'],
            confettiRadius: 3,
            confettiNumber: 100,
        },
        clap: {
            emojis: ['👏'],
            confettiRadius: 10,
            confettiNumber: 200,
        },
        heart: {
            emojis: ['❤️'],
            confettiRadius: 10,
            confettiNumber: 200,
        },

    };
    if (theme) {
        shootConfetti(modalID, configs[theme]);
    }

    if (headline) {
        $('#' + modalID + '-header-text').text(headline);
    }
    if (body) {
        $('#' + modalID + '-body-content').html(body);
    }
    showModal(modalID, config);
}

function hideMessageModal() {
    hideModal('message-modal');
}

function showMessageModal(theme, headline, body, buttonLabel, onClose=null, config=null) {
    $('#message-modal-button-label').html(buttonLabel);
    $('#message-modal-button-label').off();
    if (onClose) {
        $('#message-modal').hide();
        $('#message-modal-button-label').on('click', onClose);
    }
    showThemedModal('message-modal', theme, headline, body, config);
}

function showAlert(alertText, style='danger', elemID='alert', dismissable=true, disappearSeconds=10) {
    var css = '';
    if (disappearSeconds > 0) {
        css = 'style="-webkit-animation: cssAnimation ' + disappearSeconds + 's forwards; animation: cssAnimation ' + disappearSeconds + 's forwards;"';
    }
    if (dismissable) {
        $('#' + elemID)[0].innerHTML = '<div role="alert" class="alert alert-' + style + ' alert-dismissible" ' + css +'><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button><span id="alert-text">' + alertText + '</span></div>';    
    } else {
        $('#' + elemID)[0].innerHTML = '<div class="alert alert-' + style + '" role="alert" ' + css + '><span>' + alertText + '</span></div>';
    }
    if (disappearSeconds > 0) {
        // CSS does not remove the element and cause other UI elements blocked
        setTimeout((elemId) => {
            let alertElem = document.getElementById(elemId);
            if (alertElem) {
                alertElem.innerHTML = '';
            }
        }, (disappearSeconds + 1.0) * 1000, elemID);
    }
}

function setProgressBar(target, percent, showPercent=true, text='') {
    target.show();
    var percentBar = target.children();
    percentBar.attr('style', 'width: '+ percent.toString() + '%;');
    percentBar.attr('aria-valuenow', percent);
    if (showPercent) {
        text += Math.round(percent) + '%'
    }
    percentBar.html(text);
}

function updateProgressBar(e) {
    var percent = 100.0 * e.loaded / e.total;
    setProgressBar($('#progress-bar'), percent);
}

function clearPostSearchField() {
    $('#searchField').val('');
    OCPosts.clearSearch();
}

function initPostsSection() {
    if (isMobile()){
        collapseSidebar();
    }
    scheduler.hideQuickInfo();
    if ($('.dhx_marked_timespan')[0]){
        $('.dhx_marked_timespan')[0].scrollIntoView();
    }
}

function addLittleInput(parentElem, inputID, onEnter, onDismiss, placeholderText, inputName=null) {
    if ($('#' + inputID).length > 0) {
        return;
    }
    if (inputName === null) {
        inputName = inputID
    }
    let html = `<div class="float-right" style="width: 200px;">
  <div class="input-group float-right"><input id="` + inputID + `" name="` + inputName + `" class="form-control" type="text" style="height: 36px;" placeholder="` + placeholderText + `" />
    <div class="input-group-append"><button id="` + inputID +`-check-button" class="btn btn-primary" type="button" style="background: var(--primary-link-color);color: white;border-top-right-radius: 5px;border-bottom-right-radius: 5px;padding:0;">` + checkMarkIcon +`</button><button id="` + inputID+ `-dismiss-button" class="btn btn-dismiss-input" type="button" onclick="` + onDismiss.name + `" style="position: relative; top: 0px; right: 40px; z-index: 10; width: 20px;">x</button></div>
    </div>
</div>`;
    let wrapperNode = document.createElement('div');
    wrapperNode.id= inputID + '-wrapper';
    wrapperNode.innerHTML = html;
    parentElem.appendChild(wrapperNode);
    $('#' + inputID).keypress(function(event) {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if (keycode == '13') {
            onEnter();
        }
    });
    $('#' + inputID + '-check-button').on('click', onEnter);
    $('#' + inputID + '-dismiss-button').on('click', onDismiss);
}
