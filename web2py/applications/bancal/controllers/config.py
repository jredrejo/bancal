# -*- coding: utf-8 -*-

@auth.requires_login()
def alimentos():
    import ui_def
    ui = ui_def.uidict()
    
    db.Alimento.id.readable = False
    search_text = request.get_vars.search_text
    query = search_query(db.Alimento.id, search_text, [
                         db.Alimento.Descripcion])

    grid = SQLFORM.grid(
        query, ui=ui, search_widget=search_form, editable=False,
        deletable=False, create=False, details=False, maxtextlength=40, orderby=db.Alimento.Codigo)

    # grid = SQLFORM.smartgrid(db.Alimento,editable=False, deletable=False, create=False,details=False,maxtextlength=40)
    # grid = SQLFORM.grid(db.Alimento)

    # from plugin_solidtable import SOLIDTABLE, OrderbySelector
    # rows = db().select(db.Alimento.ALL)
    # grid = SOLIDTABLE(rows,renderstyle=True, linkto=URL('show'))

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

@auth.requires_login()
def almacen():
    db.Almacen.id.readable = False
    search_text = request.get_vars.search_text
    query = search_query(db.Almacen.id, search_text, [db.Almacen.name])

    grid = SQLFORM.grid(query, search_widget=search_form, csv=False,
                        details=False, maxtextlength=40, orderby=db.Almacen.name)

    return locals()


def get_provincias():
    q = request.vars.term
    # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
    if q:
        search_term = q.lower().replace(" ", "-")
        rows = db(db.provincia.provinciaseo.contains(
            search_term)).select(db.provincia.provincia)
        match = '\n'.join([s['provincia'] for s in rows])

        return response.json([s['provincia'] for s in rows])
    return ''


def get_poblacion():
    q = request.vars.term
    # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
    if q:
        search_term = q.lower().replace(" ", "-")
        provincia = request.args[0]
        provincia_id = db(db.provincia.provincia == provincia).select().first()
        if not provincia_id:
            rows = db(db.poblacion.poblacionseo.contains(
                search_term)).select(db.poblacion.poblacion)
        else:
            query = (db.poblacion.poblacionseo.contains(search_term))
            query = query & (db.poblacion.provincia_id == provincia_id.id)
            rows = db(query).select(db.poblacion.poblacion)
        match = '\n'.join([s['poblacion'] for s in rows])

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
    form = FORM('',

                INPUT(_name='search_text', _value=request.get_vars.keywords,

                      _style='width:200px;',
                      _id='searchText'),
                INPUT(_type='submit', _value=T('Search')),
                INPUT(_type='submit', _value=T('Clear'),
                      _onclick="jQuery('#keywords').val('');"),

                _method="GET", _action=url)

    return form


def search_query(tableid, search_text, fields):
    words = search_text.split(' ') if search_text else []
    query = tableid < 0  # empty query
    for field in fields:
        new_query = tableid > 0
        for word in words:
            new_query = new_query & field.contains(word)
        query = query | new_query
    return query
