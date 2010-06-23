pivotal-github
==============
WSGI bridge between `Pivotal Tracker`_ and `GitHub`_.


Pivotal Tracker allows any external source to be imported into its excellent
tracker for schedule tasks.  GitHub exposes their Issues via a JSON API so you
can consume it and modify it from sources other than their website.  This small
WSGI application serves as a bridge between the two of them.


Installation and Setup
----------------------

Config
""""""
The configuration is read out of a JSON file.  There's a sample in
``config.json.dist`` in the root of this project.  You need to edit it to
reflect your user, and the project you want to handle.[1]_


Running the Server
""""""""""""""""""
There's a simple ``wsgi.py`` file that runs the server.  You can run it using
your favorite WSGI handler (such as `mod_wsgi`_, `gevent`_, or `gunicorn`_).


Pivotal Setup
"""""""""""""
Inside your project, go Settings > Integrations.  At the bottom of the page
that loads is the *External Tools Integration* section.  From the *Create New
Integration...* drop-down select *Other*.

Set the *Name* to whatever you like (I'm creative and use GitHub).  Set the
*Basic Auth Username* and *Basic Auth Password* to the ``github_user`` and
``github_apikey`` fields in your ``config.json``.  The *Base URL* is optional,
but if set adds links back to GitHub.  It should be in the following format::

    http://github.com/<user>/<repo>/issues/

The final field is the URL that you've setup the WSGI server to run at.  Click
*Create* and you're set.


.. _Pivotal Tracker: http://pivotaltracker.com
.. _GitHub: http://github.com
.. _mod_wsgi: http://code.google.com/p/modwsgi/
.. _gevent: http://www.gevent.org/
.. _gunicorn: http://gunicorn.org/


.. [1] To offer this as a service, this is actually something that could be
       phased out and replaced with the internal request to handle determine
       what user/repo to pull in requests from.
