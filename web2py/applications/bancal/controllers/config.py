#!/usr/bin/python
# -*- coding: utf-8 -*-

##############################################################################
# Project:     Bancal - Gestión de almacén para los Bancos de Alimentos
# Language:    Python 2.7
# Date:        15-Ago-2013.
# Ver.:        12-Jul-2014.
# Copyright:   2013-2014 - José L. Redrejo Rodríguez  <jredrejo @nospam@ itais.net>
#
# * Dual licensed under the MIT and GPL licenses.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

#Para el autocompletado con aptana/eclipse+pydev:
if 0:
    from gluon import *
    global LOAD; LOAD  = compileapp.LoadFactory()
    global request; request = globals.Request()
    global response; response = globals.Response()
    global session; session = globals.Session()
    global cache; cache = cache.Cache()
    global db; db = sql.DAL()
    global auth; auth = tools.Auth()
    global crud; crud = tools.Crud()
    global mail; mail = tools.Mail()
    global plugins; plugins = tools.PluginManager()
    global service; service = tools.Service()


@auth.requires_login()
def alimentos():
    import ui_def
    ui = ui_def.uidict()

    db.Alimento.id.readable = False
    search_text = request.get_vars.search_text
    query = search_query(db.Alimento.id, search_text,
                         [db.Alimento.Descripcion])

    query = query & (db.Alimento.Descripcion != None)
    grid = SQLFORM.grid(
        query,
        ui=ui,
        search_widget=search_form,
        editable=True,
        paginate=30,
        csv=False,
        deletable=False,
        create=True,
        details=False,
        maxtextlength=65,
        orderby=db.Alimento.Codigo,
        )
    return locals()


@auth.requires_login()
def sede():
    record = db().select(db.Sede.ALL, limitby=(0, 1))
    if not record:
        id1 = db.Sede.insert()
    record = db(db.Sede.id == 1).select().first()

    # db.Sede.provincia.widget = SQLFORM.widgets.autocomplete(request,
    # db.provincia.provincia, limitby=(0,10), min_length=2)

    form = SQLFORM(db.Sede, record)
    if form.process().accepted:
        response.flash = 'Datos grabados'
    elif form.errors:
        response.flash = 'Hay errores en estos datos'
    else:
        response.flash = 'Rellene estos datos'

    return dict(form=form)

def cierre():
    record = db().select(db.Cierre.ALL, limitby=(0, 1))
    if not record:
        id1 = db.Cierre.insert()
    record = db(db.Cierre.id == 1).select().first()
    form = SQLFORM(db.Cierre, record)
    if form.process().accepted:
        response.flash = 'Datos grabados'
        if form.vars.Cerrado:
            session.cierre=form.vars.Fecha
        else:
            session.cierre=None
    elif form.errors:
        response.flash = 'Hay errores en estos datos'
    else:
        response.flash = 'Rellene estos datos'
    return dict(form=form)




@auth.requires_login()
def almacen():
    db.Almacen.id.readable = False
    search_text = request.get_vars.search_text
    query = search_query(db.Almacen.id, search_text, [db.Almacen.name])

    grid = SQLFORM.grid(
        query,
        search_widget=search_form,
        csv=False,
        details=False,
        maxtextlength=40,
        orderby=db.Almacen.name,
        )

    return locals()


def get_provincias():
    q = request.vars.term

    if q:
        search_term = q.lower().replace(' ', '-')
        rows = \
            db(db.provincia.provinciaseo.contains(search_term)).select(db.provincia.provincia)

        # match = '\n'.join([s['provincia'] for s in rows])

        return response.json([s['provincia'] for s in rows])
    return ''


def get_poblacion():
    q = request.vars.term

    if q:
        search_term = q.lower().replace(' ', '-')
        provincia = request.args[0]
        provincia_id = db(db.provincia.provincia
                          == provincia).select().first()
        if not provincia_id:
            rows = \
                db(db.poblacion.poblacionseo.contains(search_term)).select(db.poblacion.poblacion)
        else:
            query = db.poblacion.poblacionseo.contains(search_term)
            query = query & (db.poblacion.provincia_id
                             == provincia_id.id)
            rows = db(query).select(db.poblacion.poblacion)

        # match = '\n'.join([s['poblacion'] for s in rows])

        return response.json([s['poblacion'] for s in rows])
    return ''


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """

    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """

    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """

    return dict(form=crud())


def search_form(self, url):
    form = FORM(
        '',
        INPUT(_name='search_text', _value=request.get_vars.keywords,
              _style='width:200px;', _id='searchText'),
        INPUT(_type='submit', _value=T('Search')),
        INPUT(_type='submit', _value=T('Clear'),
              _onclick="jQuery('#keywords').val('');"),
        _method='GET',
        _action=url,
        )

    return form


def search_query(tableid, search_text, fields):
    words = (search_text.split(' ') if search_text else [])
    query = tableid < 0  # empty query
    for field in fields:
        new_query = tableid > 0
        for word in words:
            new_query = new_query & field.contains(word)
        query = query | new_query
    return query
