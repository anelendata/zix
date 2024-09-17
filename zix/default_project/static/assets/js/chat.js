/* credits
Part of the code was adopted from
https://codepen.io/bharatrpatil/pen/owNvoL
*/

let AIChat = $.fn.Chat = (function() {
    var toggleChat = function() {
        $('.chat').toggle();
        /*
        $('.prime').toggleClass('zmdi-comment-outline');
        $('.prime').toggleClass('zmdi-close');
        $('.prime').toggleClass('is-active');
        $('.prime').toggleClass('is-visible');
        $('#prime').toggleClass('is-float');
        */
        $('.chat').toggleClass('is-visible');
        $('.fab').toggleClass('is-visible');
    };

    var hideChat = function(hide) {
        $('.chat').hide();
        $('#chat_converse').css('display', 'none');
        $('#chat_body').css('display', 'none');
        $('#chat_form').css('display', 'none');
        $('.chat_login').css('display', 'block');
        $('.chat_fullscreen_loader').css('display', 'none');
        $('#chat_fullscreen').css('display', 'none');

        /*
        switch (hide) {
            case 0:
                $('#chat_converse').css('display', 'none');
                $('#chat_body').css('display', 'none');
                $('#chat_form').css('display', 'none');
                $('.chat_login').css('display', 'block');
                $('.chat_fullscreen_loader').css('display', 'none');
                $('#chat_fullscreen').css('display', 'none');
                break;
            case 1:
                $('#chat_converse').css('display', 'block');
                $('#chat_body').css('display', 'none');
                $('#chat_form').css('display', 'none');
                $('.chat_login').css('display', 'none');
                $('.chat_fullscreen_loader').css('display', 'block');
                break;
            case 2:
                $('#chat_converse').css('display', 'none');
                $('#chat_body').css('display', 'block');
                $('#chat_form').css('display', 'none');
                $('.chat_login').css('display', 'none');
                $('.chat_fullscreen_loader').css('display', 'block');
                break;
            case 3:
                $('#chat_converse').css('display', 'none');
                $('#chat_body').css('display', 'none');
                $('#chat_form').css('display', 'block');
                $('.chat_login').css('display', 'none');
                $('.chat_fullscreen_loader').css('display', 'block');
                break;
            case 4:
                $('#chat_converse').css('display', 'none');
                $('#chat_body').css('display', 'none');
                $('#chat_form').css('display', 'none');
                $('.chat_login').css('display', 'none');
                $('.chat_fullscreen_loader').css('display', 'block');
                $('#chat_fullscreen').css('display', 'block');
                break;
        }
        */
    };

    var _typeWriter = function(target, text, isHtml, pos, speed) {
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
    };

    var typeWriter = async function(target, text, isHtml=false, speed=25) {
        _typeWriter(target, text, isHtml, 0, speed);
    };

    var clearChatHistory = function() {
        _st.remove('ai_chat_history', removeCallbacks=false);
    };

    var updateChatHistory = async function() {
        var history = _st.get('ai_chat_history');
        if (!history) {
            history = [
                {
                    'role': 'assistant',
                    'content': 'Hi! I\'m ChatGPT assistant. How I can help you?',
                },
            ];
            _st.set('ai_chat_history', JSON.stringify(history), STATE_SESSION);
        } else {
            history = JSON.parse(history);
        }
        var html = '';
        var typeWriterUuid = null;
        var typeWriterMessage = null;
        history.forEach((obj, index) => {
            if (obj.role === 'assistant') {
                if (index + 1 === history.length) {
                    typeWriterUuid = uuidv4();
                    html += '<div class="chat_msg_item chat_msg_item_admin"><span id="chat-' + typeWriterUuid + '"></span>';
                    html += '<div class="chat_msg_copy_icon"><button class="btn btn-light" onclick="copyText(\'#chat-' + typeWriterUuid +'\')">' + copyIcon + '</button></div>';
                    html += '</div>';
                    typeWriterMessage = obj.content;
                } else {
                    var uuid = uuidv4();
                    html += '<div class="chat_msg_item chat_msg_item_admin"><span id="chat-' + uuid + '">' + obj.content.replaceAll(' ', '&nbsp;').replaceAll('\n', '<br>') + '</span>';
                    html += '<div class="chat_msg_copy_icon"><button class="btn btn-light" onclick="copyText(\'#chat-' + uuid +'\')">' + copyIcon + '</button></div>';
                    html += '</div>';
                }
            } else if (obj.role === 'user') {
                html += '<div><span class="chat_msg_item chat_msg_item_user">' +
                    obj.content.replaceAll(' ', '&nbsp;').replaceAll('\n', '<br>') + '</span></div>';
            }
        });
        html += '<span class="chat_msg_item "><ul class="tags"><li><a id="chat-start-over-button">Start over</a></li></ul></span>';
        $('#chat-history').html(html);
        $('#chat-start-over-button').click(function() {
            clearChatHistory();
        });
        if (typeWriterUuid) {
            typeWriter('#chat-' + typeWriterUuid, typeWriterMessage, isHtml=true, speed=15);
        }
    };

    var submit = function() {
        var message = $('#chat-message').val();
        if (!message) {
            return;
        }
        var history = _st.get('ai_chat_history');
        if (history) {
            history = JSON.parse(history);
        } else {
            history = [];
        }
        history.push({
            role: 'user',
            content: message,
        });
        _st.set('ai_chat_history', JSON.stringify(history), STATE_SESSION);
        $('#chat-message').val('');
        var data = {
            prompt: JSON.stringify(history),
        }
        var isJSON = true;
        $('#chat-history').append('<div class="chat_msg_item chat_msg_item_admin"><img style="opacity: 0.5;" src="https://social-static.anelen.co/assets/img/typing-animation.gif" width="20px"></div>');
        post(ApiPath + '/chat/general', data, [], isJSON).then(response => {
            history.push(response.data.response);
            _st.set('ai_chat_history', JSON.stringify(history), STATE_SESSION);
        }, error => {
            showAlert(error.toString(), 'danger');
        });
    };

    var initView = function(cssPath) {
        $(cssPath).html(`
        <div class="chat">
          <div class="chat_header">
            <div class="chat_option">
              <div class="header_img">
                <img/>
              </div>
              <span id="chat_head">ChatGPT</span> <br> <span class="agent">Your Assitant</span>
            </div>
            <span id="chat-dismiss" class="chat_dismiss">` + dismissIcon + `</span>
          </div>
          <div id="chat-history" class="chat_body chat_login chat_conversion chat_converse">
          </div>
          <div class="fab_field">
            <textarea id="chat-message" name="chat_message" placeholder="Send a message" class="chat_field chat_message"></textarea>
            <a id="chat-send" class="fab chat-send">` + paperPlane + `</a>
          </div>
        </div>
        `);
        $('.chat').hide();
    };

    var initCallbacks = function(
            chatOpenButton='#chat-open',
            chat_dismiss_button='#chat-dismiss',
            chat_send_button='#chat-send',
        ) {
        _st.addCB('ai_chat_history', updateChatHistory);

        $(chatOpenButton).click(function() {
            toggleChat();
        });
        $(chat_dismiss_button).click(function() {
            toggleChat();
        });
        $(chat_send_button).click(function() {
            submit();
        });
        /*
        $('#chat_first_screen').click(function(e) {
            hideChat(1);
        });
        $('#chat_second_screen').click(function(e) {
            hideChat(2);
        });
        $('#chat_third_screen').click(function(e) {
            hideChat(3);
        });
        $('#chat_fourth_screen').click(function(e) {
            hideChat(4);
        });
        */
    };

    // Exposing private members
    return {
        init: function(cssPath='#chat-div', buttonPath='#chat-sidebar-link') {
            initView(cssPath);
            hideChat(0);
            initCallbacks(chatOpenButton=buttonPath);
            updateChatHistory();
        },
    };
})();
