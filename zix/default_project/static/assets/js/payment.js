let OCPayment= $.fn.Payment = (function() {
    // private properties
    const namespace = 'OCPayment';

    // private methods
    var initView = function() {
    };

    var initCallbacks = function() {
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
                handleHttpError(error);
            }
        }, function(error) {
            handleHttpError(error);
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
                handleHttpError(error);
            }
        }, function(error) {
            handleHttpError(error);
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
                handleHttpError(error);
            }
        }, function(error) {
            handleHttpError(error);
        });
    };

    var _isFeatureActive = function(feature='core') {
        let me = _st.get('me');
        if (!me) {
            // too early to call
            return null;
        }
        if (me.is_demo) {
            return false;
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
        let me = _st.get('me');
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
            var accountUid = _st.get('acccount_uid', _st.get('me').account.uid);
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

    // This isn't used
    var _updatePaymentHistory = function() {
        var row = '<tr><td>' + paymentDate + '</td><td><span>' + paymentPlan + '</span></td><td>' + paymentDescription + '</td><td><button class="btn btn-primary" type="button" onclick="">View on' + stripeIcon + '</button></td></tr>';
    };

    // Exposing private members
    return {
        init: function() {
            // Check requirement
            /*
            if ((typeof OCLinkedIn === 'undefined')) {
                throw new Error('This module requires OCLinkedIn.');
            }
            */
            initView();
            initCallbacks();
        },
        isFeatureActive: function(feature = 'core') {
            return _isFeatureActive(feature);
        },
        checkSubscription: function() {
            _checkSubscription();
        }
    };
})();
