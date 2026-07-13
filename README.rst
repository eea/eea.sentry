==========
eea.sentry
==========
.. image:: https://ci.eionet.europa.eu/buildStatus/icon?job=eea/eea.sentry/develop
  :target: https://ci.eionet.europa.eu/job/eea/job/eea.sentry/job/develop/display/redirect
  :alt: Develop
.. image:: https://ci.eionet.europa.eu/buildStatus/icon?job=eea/eea.sentry/master
  :target: https://ci.eionet.europa.eu/job/eea/job/eea.sentry/job/master/display/redirect
  :alt: Master

Sentry integration for Plone and Zope

.. contents::


Main features
=============
It comes with plenty of configuration options and features like:

1. Easy to install/uninstall via Site Setup > Add-ons;
2. Easily setup Sentry integration via environment variables;
3. Report Python/Javascript errors to Sentry.


Install
=======

* Add eea.sentry to your eggs section in your buildout and re-run buildout::

    [buildout]
    eggs +=
      eea.sentry

    zcml +=
      eea.sentry

* You can download a sample buildout from:

  - https://github.com/eea/eea.sentry/tree/master/buildouts/zope2
  - https://github.com/eea/eea.sentry/tree/master/buildouts/plone4
  - https://github.com/eea/eea.sentry/tree/master/buildouts/plone5

* Or via docker::

    $ docker run --rm -p 8080:8080 -e ADDONS="eea.sentry" -e SENTRY_DSN="https://<public_key>:<secret_key>@sentry.io" plone

* Plone:

  * Within Site Setup > Add-ons install eea.sentry

* Zope:

  * Add the following lines within your ZPT files / main_template::

      <!-- Sentry start -->
      <div tal:replace="structure context/@@sentry" />
      <script type="text/javascript" src="/++resource++sentry.min.js"></script>
      <script type="text/javascript" src="/++resource++sentry.js"></script>
      <!-- Sentry end -->


Environment variables
=====================

In order to start sending error logs to sentry you'll need to provide the following environment variables to your Zope/Plone instance:

* **SENTRY_DSN** - Send python tracebacks to sentry.io or your custom Sentry installation (e.g.: **SENTRY_DSN=https://<public_key>:<secret_key>@sentry.example.com**)
* **SENTRY_SITE**, **SERVER_NAME** - Add **site** tag to Sentry logs (e.g.: **SENTRY_SITE=foo.example.com**)
* **SENTRY_RELEASE**, **EEA_KGS_VERSION** - Add **release** tag to Sentry logs (e.g.: **SENTRY_RELEASE=5.1.5-34**)
* **SENTRY_ENVIRONMENT** - Add **environment** tag to Sentry logs. Leave empty to automatically get it from rancher-metadata (e.g.: **SENTRY_ENVIRONMENT=staging**)


Buildout installation
=====================

- `Zope 2 <https://github.com/eea/eea.sentry/tree/master/buildouts/zope2>`_
- `Plone 4+ <https://github.com/eea/eea.sentry/tree/master/buildouts/plone4>`_
- `Plone 5+ <https://github.com/eea/eea.sentry/tree/master/buildouts/plone5>`_


Source code
===========

- `Plone 4+ on github <https://github.com/eea/eea.sentry>`_
- `Plone 5+ on github <https://github.com/eea/eea.sentry>`_


Eggs repository
===============

- https://pypi.python.org/pypi/eea.sentry
- http://eggrepo.eea.europa.eu/simple


Plone versions
==============
It has been developed and tested for Plone 4 and 5. See buildouts section above.


How to contribute
=================
See the `contribution guidelines (CONTRIBUTING.md) <https://github.com/eea/eea.sentry/blob/master/CONTRIBUTING.md>`_.

Copyright and license
=====================

eea.sentry (the Original Code) is free software; you can
redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc., 59
Temple Place, Suite 330, Boston, MA 02111-1307 USA.

The Initial Owner of the Original Code is European Environment Agency (EEA).
Portions created by Eau de Web are Copyright (C) 2009 by
European Environment Agency. All Rights Reserved.


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: https://www.eea.europa.eu/
.. _`EEA Web Systems Training`: http://www.youtube.com/user/eeacms/videos?view=1

Secret Scanning
===============

This repository uses the Betterleaks GitHub Action to scan the current
repository content on every push and pull request. The scan uses the rules in
``.gitleaks.toml`` and uploads a ``betterleaks-report`` artifact when a finding
is detected.

If the optional SMTP secrets are configured, failed scans also send an email to
the last commit committer. The workflow expects these repository or
organization secrets:

- ``SMTP_URL``
- ``SMTP_PORT`` (optional, defaults to ``25``)
- ``SMTP_EMAIL``
- ``SMTP_PASSWORD`` (optional if the SMTP server does not require authentication)

Port ``465`` is sent with direct TLS; other ports use the default SMTP
handshake. The email includes a short finding summary from the redacted
Betterleaks report, including the redacted matched line from each finding.

There are three common outcomes:

1. Everything is OK. The ``Betterleaks / Scan for secrets`` check is green and
   no action is needed. Regular references to runtime values are OK, for example::

     token_from_cookie = request.cookies.get("auth_token")

2. A real secret was found. The check is red and the workflow log asks you to
   download the ``betterleaks-report`` artifact. Open the artifact from the
   GitHub Actions run and check the reported file, line and rule. Remove the
   committed value, move it to the proper secret store, and rotate it if it was
   exposed. A report entry looks like this::

     {
       "RuleID": "secret-literal-assignment",
       "File": "src/config.py",
       "StartLine": 12,
       "Secret": "[REDACTED]"
     }

3. The finding is a false positive. Keep the value only if it is clearly not
   sensitive, such as a test fixture, placeholder, or public example. Add
   ``betterleaks:allow`` on the same line and include a short explanation in the
   pull request::

     test_password = "admin"  #betterleaks:allow

Do not add ``betterleaks:allow`` to real credentials.
