let Payment= $.fn.Payment = (function() {
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
    const namespace = 'Payment';

    // private methods
    let _initView = function() {
    };

    let _setUICallbacks = function() {
        // personal
        $('#payment-terms-checkbox').change(function() {
            if (this.checked) {
                $('#payment-submit-button').removeClass('disabled');
                $('#payment-submit-button').removeAttr('disabled');
            } else {
                $('#payment-submit-button').prop('disabled', true);
            }
        });
        $('#payment-submit-button').on('click', function() {
            _stripeCheckoutPersonal();
        });

        // organization
        $('#org-payment-terms-checkbox').change(function() {
            if (this.checked) {
                $('#org-payment-submit-button').removeClass('disabled');
                $('#org-payment-submit-button').removeAttr('disabled');
            } else {
                $('#org-payment-submit-button').prop('disabled', true);
            }
        });
        $('#org-payment-submit-button').on('click', function() {
            _stripeCheckoutOrganization();
        });

        $('#stripe-portal-button').on('click', function() {
            _goToStripePortal();
        });
        $('#payment-issue-modal-stripe-portal-button').on('click', function() {
            _goToStripePortal();
        });
    };

    var _stripeCheckoutPersonal = function() {
        var priceId = $('#annual-plan-radio-button')[0].value;
        if ($('#monthly-plan-radio-button').prop("checked")) {
            priceId = $('#monthly-plan-radio-button')[0].value;
        }
        var featureName = $('#payment-feature-name-input')[0].value;
        var accountUid = $('#payment-account-uid-input')[0].value;
        var data = {
            'price_id': priceId,
            'feature_name': featureName,
            'account_uid': accountUid,
        }
        var isJSON = true;
        var isAsync = false;
        post(ApiPath + '/payment/checkout/session', data, [], isJSON, isAsync).then(response => {
            if (response.state === 'success') {
                window.location.href = response.data.url;
            } else {
                AppView.handleHttpError(error);
            }
        }, function(error) {
            AppView.handleHttpError(error);
        });
    };

    var _stripeCheckoutOrganization = function() {
        var priceId = $('#org-monthly-plan-input')[0].value;
        var featureName = $('#org-payment-feature-name-input')[0].value;
        var accountUid = $('#payment-account-uid-input')[0].value;
        let orgName = $('#org-name');
        var data = {
            'org_name': orgName,
            'price_id': priceId,
            'feature_name': featureName,
            'account_uid': accountUid,
        }
        var isJSON = true;
        var isAsync = false;
        post(ApiPath + '/payment/checkout/session', data, [], isJSON, isAsync).then(response => {
            if (response.state === 'success') {
                window.location.href = response.data.url;
            } else {
                AppView.handleHttpError(error);
            }
        }, function(error) {
            AppView.handleHttpError(error);
        });
    };

    var _goToStripePortal = function() {
        var data = {
        }
        var isJSON = true;
        var isAsync = false;
        post(ApiPath + '/payment/portal/session', data, [], isJSON, isAsync).then(response => {
            if (response.state === 'success') {
                window.location.href = response.data.url;
            } else {
                AppView.handleHttpError(error);
            }
        }, function(error) {
            AppView.handleHttpError(error);
        });
    };

    var _isFeatureActive = function(feature='core') {
        let me = App.getState().get('me');
        if (!me) {
            // too early to call
            return null;
        }
        let hasCore = false;
        const inActiveStatus = ['past_due', 'incomplete', 'incomplete_expired', 'paused'];
        // Check subscription
        me.feature_subscriptions.filter(obj=>{
            return (
                obj.feature.name === feature &&
                (
                    (!obj.start_on || moment.utc(obj.start_on) <= moment()) &&
                    (!obj.end_on || moment() < moment.utc(obj.end_on)) &&
                    !inActiveStatus.includes(obj.payment.status)
                )
            );
        }).forEach((obj, index) => {
            hasCore = true;
        });
        return hasCore;
    };

    var _checkSubscription = function() {
        let me = App.getState().get('me');
        if (!me) return;
        // Check subscription
        let hasCore = false;
        let paymentIssue = null;
        let featureHtml = '';
        me.feature_subscriptions.forEach((obj, index) => {
            var endOn = null;
            var endOnStr = 'Not set';
            if (obj.end_on) {
                endOn = moment.utc(obj.end_on);
                endOnStr = endOn.format('YYYY-MM-DD hh:mmaZ')
            }
            featureHtml += '<tr><td>' +  obj.feature.name + '</td><td>' + obj.payment.plan.description + '</td><td>' + endOnStr + '</td></tr>';
            if (obj.feature.name === 'core') {
                var startOn = moment();
                if (obj.start_on) {
                    startOn = moment.utc(obj.start_on);
                }
                var endOn = null;
                if (obj.end_on) {
                    endOn = moment.utc(obj.end_on);
                }
                if (startOn <= moment() && (endOn === null || moment() <= endOn)) {
                    hasCore = true;
                }
                if (obj.is_active && obj.payment
                    && obj.payment.status && !obj.payment.status.includes('active', 'trialing')
                ) {
                    paymentIssue = obj.payment.status;
                }
            }
        });
        $('#subscriptions-table-body').html(featureHtml);
        if (!hasCore) {
            var accountUid = App.getState().get('acccount_uid', App.getState().get('me').account.uid);
            var featureName = 'core';
            me.payment_plans.forEach((obj, index) => {
                if (obj.billing_cycle === 1) {
                    $('#monthly-field-label').html(obj.description);
                    $('#monthly-plan-radio-button')[0].value = obj.app_price_id;
                } else if (obj.billing_cycle === 2) {
                    $('#annual-field-label').html(obj.description);
                    $('#annual-plan-radio-button')[0].value = obj.app_price_id;
                }
            });
            $('#payment-account-uid-input')[0].value = accountUid;
            $('#payment-feature-name-input')[0].value = featureName;
            showModal('payment-modal');
            return;
        }
        if (paymentIssue && paymentIssue != 'canceled') {
            showModal('payment-issue-modal');
            return;
        }
        hideModal('payment-modal');
        hideModal('payment-issue-modal');
    };

    let _onMeChange = function(me) {
        _checkSubscription();                                          
    };

    // Exposing private members
    return {
        init: function() {
            _initView();
            _setStateCallBacks();
            _setUICallbacks();
        },
        isFeatureActive: function(feature = 'core') {
            return _isFeatureActive(feature);
        },
    };
})();
