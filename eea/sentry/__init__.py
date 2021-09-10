""" Main product initializer
"""
import os
import six
import logging
from contextlib import closing
import sentry_sdk
from sentry_sdk import set_user
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.users import nobody
from zope.i18nmessageid.message import MessageFactory
from zope.globalrequest import getRequest
if six.PY2:
    from eventlet.green import urllib2 as request
else:
    from eventlet.green.urllib import request
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface.interfaces import ComponentLookupError

from ZPublisher.HTTPRequest import _filterPasswordFields

EEAMessageFactory = MessageFactory('eea')
logger = logging.getLogger()


def environment():
    """ Try to get environment from rancher-metadata
    """
    url = "http://rancher-metadata/latest/self/stack/environment_name"
    try:
        with closing(request.urlopen(url)) as conn:
            env = conn.read()
    except Exception as err:
        logger.warn("Couldn't get environ from rancher-metadata: %s.", err)
        env = "devel"
    return env


def _get_user_from_request(request):
    user = request.get("AUTHENTICATED_USER", None)

    if user is None:
        user = getSecurityManager().getUser()

    if user is not None and user != nobody:
        user_dict = {
            "id": user.getId(),
            "email": user.getProperty("email") or "",
        }
    else:
        user_dict = {'id': 'Anonymous'}

    return user_dict


def _get_other_from_request(request):
    other = {}
    for k, v in _filterPasswordFields(request.other.items()):
        if k in ("PARENTS", "RESPONSE"):
            continue
        other[k] = repr(v)
    return other


def _get_lazyitems_from_request(request):
    lazy_items = {}
    for k, v in _filterPasswordFields(request._lazies.items()):
        lazy_items[k] = repr(v)
    return lazy_items


def _get_cookies_from_request(request):
    cookies = {}
    for k, v in _filterPasswordFields(request.cookies.items()):
        cookies[k] = repr(v)
    return cookies


def _get_form_from_request(request):
    form = {}
    for k, v in _filterPasswordFields(request.form.items()):
        form[k] = repr(v)
    return form


def _get_request_from_request(request):
    # ensure that all header key-value pairs are strings
    headers = dict()
    for k, v in request.environ.items():
        if not isinstance(v, str):
            v = str(v)
        headers[k] = v

    body_pos = request.stdin.tell()
    request.stdin.seek(0)
    request.stdin.seek(body_pos)
    http = dict(
        headers=headers,
        url=request.getURL(),
        method=request.method,
        host=request.environ.get("REMOTE_ADDR", ""),
    )
    if "HTTP_USER_AGENT" in http["headers"]:
        if "User-Agent" not in http["headers"]:
            http["headers"]["User-Agent"] = http["headers"]["HTTP_USER_AGENT"]
    if "QUERY_STRING" in http["headers"]:
        http["query_string"] = http["headers"]["QUERY_STRING"]

    return http


def _before_send(event, hint):
    """
     Inject Plone/Zope specific information (based on raven.contrib.zope)
    """
    request = getRequest()

    if request:
        # We have no request if event is captured by errorRaisedSubscriber
        # (see below) so extra information must be set there.
        # If the event is send by pythons logging module
        #  we set extra info here.
        if "other" not in event["extra"]:
            event["extra"]["other"] = _get_other_from_request(request)
        if "lazy items" not in event["extra"]:
            event["extra"]["lazy items"] = _get_lazyitems_from_request(request)
        if "cookies" not in event["extra"]:
            event["extra"]["cookies"] = _get_cookies_from_request(request)
        if "form" not in event["extra"]:
            event["extra"]["form"] = _get_form_from_request(request)
        if "request" not in event["extra"]:
            event["extra"]["request"] = _get_request_from_request(request)
        user_info = _get_user_from_request(request)
        set_user(user_info)

    return event


def before_send(event, hint):
    try:
        return _before_send(event, hint)
    except KeyError:
        logging.warning("Could not extract data from request", exc_info=True)


def initialize(context):
    """ Initializer """
    try:
        registry = getUtility(IRegistry)
        import pdb;pdb.set_trace()
    except ComponentLookupError:
        # we don't yet have traversal context
        pass

    sentry_dsn = os.environ.get('SENTRY_DSN', '')
    if not sentry_dsn:
        return
    sentry_sdk.init(
        sentry_dsn,
        max_breadcrumbs=50,
        before_send=before_send,
        release=os.environ.get('SENTRY_RELEASE',
                               os.environ.get('EEA_KGS_VERSION', 'dev')),
        environment=os.environ.get("SENTRY_ENVIRONMENT", environment()),
        traces_sample_rate=1.0,
    )
    sentry_sdk.set_context("additional", {
        'site': os.environ.get('SENTRY_SITE',
                               os.environ.get('SERVER_NAME', "dev")),
    })
    request = getRequest()
    if request:
        user_info = _get_user_from_request(request)
        sentry_sdk.set_user(user_info)
