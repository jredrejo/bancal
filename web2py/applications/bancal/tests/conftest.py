#!/usr/bin/env python

''' py.test configuration and fixtures file.

Tells application she's running in a test environment.
Creates a complete web2py environment, similar to web2py shell.
Creates a WebClient instance to browse your application, similar to a real
web browser.
Propagates some application data to test cases via fixtures, like baseurl and
automatic appname discovering.
'''

import os
import pytest
import sys

sys.path.insert(0, '')

@pytest.fixture(scope='session')
def baseurl(appname):
    '''The base url to call your application.

    Change you port number as necessary.
    '''

    return 'http://localhost:8000/%s' % appname


@pytest.fixture(scope='session')
def appname():
    '''Discover application name.

    Your test scripts must be on applications/<your_app>/tests
    '''

    dirs = os.path.split(__file__)[0]
    appname = dirs.split(os.path.sep)[-2]
    return appname


@pytest.fixture(scope='session', autouse=True)
def create_testfile_to_application(request, appname):
    '''Creates a temp file to tell application she's running under a
    test environment.

    Usually you will want to create your database in memory to speed up
    your tests and not change your development database.

    This fixture is automatically run by py.test at session level. So, there's
    no overhad to test performance.
    '''

    from ..modules.web2pytest import web2pytest
    web2pytest.create_testfile(appname)

    request.addfinalizer(web2pytest.delete_testfile)


@pytest.fixture(scope='session')
def cleanup_db(web2py):
    '''Truncate all database tables before every single test case.

    This can really slow down your tests. So, keep your test data small and try
    to allocate your database in memory.

    Automatically called by test.py due to decorator.
    '''
    return
    web2py.db.rollback()
    for tab in web2py.db.tables:
        web2py.db[tab].truncate()
    web2py.db.commit()


@pytest.fixture()
def web2py(appname):
    '''Create a Web2py environment similar to that achieved by
    Web2py shell.

    It allows you to use global Web2py objects like db, request, response,
    session, etc.

    Concerning tests, it is usually used to check if your database is an
    expected state, avoiding creating controllers and functions to help
    tests.
    '''

    def run(controller, function, env):
        """Injects request.controller and request.function into
        web2py environment.
        """

        from gluon.compileapp import run_controller_in

        env.request.controller = controller
        env.request.function = function
        r = None
        try:
            r =  run_controller_in(controller, function, env)
        except HTTP as e:
            if str(e.status).startswith("2") or str(e.status).startswith("3"):
                env.db.commit()
            raise
        else:
            env.db.commit()
        finally:
            env.db.rollback()
        return r


    def submit(controller, action, env, data=None, formname=None):
        """Submits a form, setting _formkey and _formname accordingly.

        env must be the web2py environment fixture.
        """

        formname = formname or "default"

        hidden = dict(
            _formkey=action,
            _formname=formname
        )

        if data:
            env.request.post_vars.update(data)
        env.request.post_vars.update(hidden)
        env.session["_formkey[%s]" % formname] = [action]

        return env.run(controller, action, env)


    from gluon.shell import env
    from gluon.storage import Storage

    web2py_env = env(appname, import_models=True,
                     extra_request=dict(is_local=True,
                                        _running_under_test=True))

    del web2py_env['__file__']  # avoid py.test import error
    web2py_env['run'] = run
    web2py_env['submit'] = submit
    globals().update(web2py_env)

    return Storage(web2py_env)
