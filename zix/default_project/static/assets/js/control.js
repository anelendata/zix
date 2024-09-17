function getActiveAccount() {
    let active_acct_uid = App.getState().get('active_account_uid');
    let me = App.getState().get('me');
    if (!me) return null;
    let activeAccount = me.account;

    if (me.account.uid != active_acct_uid) {
        me.account.memberships.filter(m=>{return m.account.uid == active_acct_uid;}).forEach(m=> {
            activeAccount = m.account;
        });
    }
    return activeAccount;
}
