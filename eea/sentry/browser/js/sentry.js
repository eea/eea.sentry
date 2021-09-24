document.addEventListener("DOMContentLoaded", function(){
    var context = document.getElementById("sentry");
    if(!context) {
        context = document.getElementsByTagName("body")[0];
    }

    var sentry_dsn = context.getAttribute("data-sentry-dsn");
    var sentry_env = context.getAttribute("data-sentry-env");
    var sentry_ver = context.getAttribute("data-sentry-ver");
    var sentry_site = context.getAttribute("data-sentry-site");
    var sentry_server = context.getAttribute("data-sentry-server");
    var sentry_user = context.getAttribute("data-sentry-user");
    try {
        sentry_user = JSON.parse(sentry_user);
    } catch (err) {
        sentry_user = {};
    }

    if (sentry_dsn){
        Sentry.init({
            dsn: sentry_dsn,
            release: sentry_ver,
            environment: sentry_env,
            integrations: [new Sentry.Integrations.BrowserTracing()],
            tracesSampleRate: 1.0,
            attachStacktrace: true,
            ignoreErrors: [
                'jQuery is not defined',
                 '$ is not defined',
                 'Can\'t find variable: jQuery',
                 'Socialite is not defined',
                 'Persistent storage maximum size reached'
            ],
            logger: 'javascript',
            serverName: sentry_server,
            tags: {
                site: sentry_site
            }
        });
        Sentry.setUser(sentry_user);
    }
});
