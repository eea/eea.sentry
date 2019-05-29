$(function(){
    var sentry_dsn = $('#sentry').data('sentry-dsn') || $('body').data('sentry-dsn');
    var sentry_env = $('#sentry').data('sentry-env') || $('body').data('sentry-env');
    var sentry_ver = $('#sentry').data('sentry-ver') || $('body').data('sentry-ver');
    var sentry_user = $('#sentry').data('sentry-user') || $('body').data('sentry-user');
    var sentry_site = $('#sentry').data('sentry-site') || $('body').data('sentry-site');
    var sentry_server = $('#sentry').data('sentry-server') || $('body').data('sentry-server');

    if (sentry_dsn){
        Raven.config(sentry_dsn, {
            logger: 'javascript',
            release: sentry_ver,
            environment: sentry_env,
            serverName: sentry_server,
            tags: {
                site: sentry_site
            },
            ignoreErrors: [
                'jQuery is not defined',
                 '$ is not defined',
                 'Can\'t find variable: jQuery',
                 'Socialite is not defined',
                 'Persistent storage maximum size reached'
            ]
        }).install();
        Raven.setUserContext(sentry_user);
    }
});
