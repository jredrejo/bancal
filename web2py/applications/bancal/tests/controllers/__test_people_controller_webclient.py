#!/usr/bin/env python

'''py.test test cases to test people application.

These tests run based on webclient and need web2py server running.

If you want to see a faster approach, see test_people_controller_web2pyenv.py
in this same directory.
'''


def test_index_exists(client):
    '''page index exists?
    '''

    client.get('/people/index') # get a page
    assert client.status == 200
    assert "hi. i'm the people index" in client.text.lower()


def test_new_person_with_form(client):
    '''Is this function showing the right form?
    '''

    client.get('/people/new_person')
    assert 'new_person_form' in client.forms
    assert 'name="name"' in client.text
    assert 'name="phone"' in client.text
    assert 'name="created_at"' not in client.text # just ones listed in SQLFORM

    # In case of widgets, I recommend you use re.findall() or re.search() to
    # see if your field was rendered using the right HTML tag.
    # Examples: <input type="text"...>, <input type="checkbox"...>,
    # <textarea...>, etc.


def test_validate_new_person(client, web2py):
    '''Is the form validating?
    '''

    data = dict(name='',
                phone='',
                _formname='new_person_form')
    client.post('/people/new_person', data=data) # post data
    assert client.status == 200

    assert 'name__error' in client.text
    assert 'phone__error' in client.text

    assert web2py.db(web2py.db.people).count() == 0

    # You can create other test case to check other validations, too.


def test_save_new_person(client, web2py):
    '''Created a new person?
    '''

    data = dict(name='Homer Simpson',
                phone='9988-7766',
                _formname='new_person_form')
    client.post('/people/new_person', data=data)
    assert client.status == 200

    assert 'New person saved' in client.text

    assert web2py.db(web2py.db.people).count() == 1
    assert web2py.db(web2py.db.people.name == data['name']).count() == 1


def test_get_person_by_creation_date(client, web2py):
    '''Is my filter working?
    '''

    from gluon.contrib.populate import populate
    populate(web2py.db.people, 3) # insert 3 persons with random data
    web2py.db.commit()
    assert web2py.db(web2py.db.people).count() == 3

    data = dict(
            name='John Smith',
            phone='3322-4455',
            created_at='1999-04-03 18:00:00')

    web2py.db.people.insert(**data) # insert my controlled person
    web2py.db.commit()

    client.get('/people/get_by_creation_date.json/' +
            data['created_at'].split()[0])
    assert client.status == 200
    assert 'application/json' in client.headers['content-type']

    import json
    person = json.loads(client.text)
    assert person['name'] == data['name']
