# -*- coding: utf-8 -*-
import pytest


@pytest.fixture()
def insertar_entrada(request):
    db = web2py.db
    entrada_id = db.CabeceraEntrada.insert(tipoProcedencia="DISTRIBUCIÓN", Donante=1)
    db.



def test_hay_stock(web2py):
    db = web2py.db
    hay = 0

    query = (db.CabeceraAlmacen.alimento == db.Alimento.id) \
        & (db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera) \
        & (db.Alimento.Descripcion != None)

    rows = db(query).select(
        db.CabeceraAlmacen.id,
        db.Alimento.Codigo,
        db.Alimento.Descripcion,
        db.Alimento.Conservacion,
        db.Alimento.Unidades,
        db.LineaAlmacen.Stock.sum(),
        groupby=db.CabeceraAlmacen.alimento,
    )
    for row in rows:
        if row[db.LineaAlmacen.Stock.sum()] > 0:
            hay += 1
            break

    assert hay > 0


def kktest_index_exists(web2py):
    '''Page index exists?
    '''

    # run the controller, without view
    result = web2py.run('people', 'index', web2py)

    # now, render the view with context received from controller
    html = web2py.response.render('people/index.html', result)
    assert "Hi. I'm the people index" in html


def kktest_new_person_with_form(web2py):
    '''Is this function showing the right form?
    '''

    result = web2py.run('people', 'new_person', web2py)

    html = web2py.response.render('people/new_person.html', result)

    assert 'new_person_form' in html
    assert 'name="name"' in html
    assert 'name="phone"' in html
    assert 'name="created_at"' not in html  # just ones listed in SQLFORM

    # In case of widgets, I recommend you use re.findall() or re.search() to
    # see if your field was rendered using the right HTML tag.
    # Examples: <input type="text"...>, <input type="checkbox"...>,
    # <textarea...>, etc.


def kktest_validate_new_person(web2py):
    '''Is the form validating?
    '''

    data = dict(
        name='',
        phone='',
    )

    result = web2py.submit('people', 'new_person', web2py, data,
                           formname='new_person_form')

    assert result['form'].errors

    html = web2py.response.render('people/new_person.html', result)

    assert 'name__error' in html
    assert 'phone__error' in html

    assert web2py.db(web2py.db.people).count() == 0

    # You can create other test case to check other validations, too.


def kktest_save_new_person(web2py):
    '''Created a new person?
    '''

    data = dict(
        name='Homer Simpson',
        phone='9988-7766',
    )

    result = web2py.submit('people', 'new_person', web2py, data,
                           formname='new_person_form')

    html = web2py.response.render('people/new_person.html', result)

    assert 'New person saved' in html

    assert web2py.db(web2py.db.people).count() == 1
    assert web2py.db(web2py.db.people.name == data['name']).count() == 1


def kktest_get_person_by_creation_date(web2py):
    '''Is my filter working?
    '''

    from gluon.contrib.populate import populate
    populate(web2py.db.people, 3)  # insert 3 persons with random data
    assert web2py.db(web2py.db.people).count() == 3

    data = dict(
        name='John Smith',
        phone='3322-4455',
        created_at='1999-04-03 18:00:00')

    web2py.db.people.insert(**data)  # insert my controlled person
    web2py.db.commit()

    web2py.request.args.append(data['created_at'].split()[0])

    result = web2py.run('people', 'get_by_creation_date', web2py)

    # test controller result
    assert result['name'] == data['name']

    # test controller result rendered as json by a view
    web2py.request.extension = 'json'
    html = web2py.response.render('people/get_by_creation_date.json', result)
    import json
    person = json.loads(html)
    assert person['name'] == data['name']
    assert person['created_at'] == data['created_at']
