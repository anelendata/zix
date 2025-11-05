const Config = {
    apiPath: '/api/v1',
    namespace: 'ZixCore',
    supportEmail: 'support@anelen.co',
    pages: {
        'tab-1': {
            menuIcon: Icons.edit,
            menuDisplay: 'Tab 1',
            contentURL: '/assets/pages/tab_1.html',
            onLoad: undefined,
            onStart: undefined,
        },
        settings: {
            menuIcon: Icons.cog,
            menuDisplay: 'Settings',
            onLoad: undefined,
            onStart: undefined,
        },
        help: {
            menuIcon: Icons.heartShield,
            menuDisplay: 'Help',
            onLoad: undefined,
            onStart: undefined,
        },
    },
};