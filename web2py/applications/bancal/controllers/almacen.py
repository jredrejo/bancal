# -*- coding: utf-8 -*-
import math
if 0:
    from gluon import *

@auth.requires_login()
def stock():
    session.AlmacenFamilia = None
    session.AlmacenSubFamilia = None
    session.AlmacenAlimento = None
    db.Alimento.Descripcion.widget = ajax_autocomplete
    form = SQLFORM(db.Alimento)
    # if request.vars.Descripcion:
    #    session.AlmacenAlimento=request.vars.Descripcion
    response.files.append(
        URL(r=request, c='static/jqGrid/js/i18n', f='grid.locale-es.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/js', f='jquery.jqGrid.min.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/css', f='ui.jqgrid.css'))

    response.flash = 'Escriba el alimento o elija la familia o subfamilia'

    return locals()


@auth.requires_login()
def entradas():
    session.FechaAlmacen = None
    session.DonanteAlmacen =None
    session.ProcedenciaAlmacen = None
    session.AlmacenAlimento = None
    db.Alimento.Descripcion.widget = ajax_autocomplete
    form = SQLFORM(db.CabeceraEntrada)
    
    # if request.vars.Descripcion:
    #    session.AlmacenAlimento=request.vars.Descripcion
    response.files.append(
        URL(r=request, c='static/jqGrid/js/i18n', f='grid.locale-es.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/js', f='jquery.jqGrid.min.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/css', f='ui.jqgrid.css'))

    return locals()


@service.json
def get_codigo():
    codigo=request.vars.codigo
    alimento=db(db.Alimento.Codigo==codigo).select().first()
    if alimento:
        data = {"alimento":alimento.Descripcion}
        session.AlmacenAlimento = alimento.id
    else:
        data ={"alimento":''}
    return response.json(data)


@service.json
def set_alimento():
    codigo=''
    if len(request.vars) > 0:
        session.AlmacenAlimento = request.vars.alimento        
        alimento=db(db.Alimento.Descripcion==request.vars.alimento).select().first()
        if alimento:
            codigo=alimento.Codigo
            session.AlmacenAlimento =alimento.id
    if codigo =='': session.AlmacenAlimento=None
    return response.json(codigo)  

@service.json
def get_rows():
    """ this gets passed a few URL arguments: page number, and rows per page, and sort column, and sort desc or asc
    """

    fields = ['Alimento.Descripcion', 'Alimento.Familia',
              'Alimento.SubFamilia', 'Alimento.Conservacion', 'Stock', 'Alimento.Unidades']
    rows = []
    page = int(request.vars.page)  # the page number
    pagesize = int(request.vars.rows)

    limitby = (page * pagesize - pagesize, page * pagesize)

    if request.vars.sidx == 'Stock':
        orderby = db.LineaAlmacen.Stock.sum()
    else:
        orderby = db.Alimento[request.vars.sidx]
    if request.vars.sord == 'desc':
        orderby = ~orderby
    query = (db.CabeceraAlmacen.alimento == db.Alimento.id) & (
        db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)

    if session.AlmacenFamilia:
        query = query & (db.Alimento.Familia == session.AlmacenFamilia)
    if session.AlmacenSubFamilia:
        query = query & (db.Alimento.SubFamilia == session.AlmacenSubFamilia)
    if session.AlmacenAlimento:
        query = query & (db.Alimento.Descripcion == session.AlmacenAlimento)
    for r in db(
        query).select(db.CabeceraAlmacen.id, db.Alimento.Descripcion, db.Alimento.Familia,
                      db.Alimento.SubFamilia, db.Alimento.Conservacion, db.Alimento.Unidades, db.LineaAlmacen.Stock.sum(
                      ),
                      limitby=limitby, orderby=orderby, groupby=db.CabeceraAlmacen.alimento):
        # print db._lastsql
        vals = []
        for f in fields:
            # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
            if f == 'Alimento.Familia':
                vals.append(db.Alimento['Familia'].represent(r(f)))
            elif f == 'Alimento.SubFamilia':
                vals.append(db.Alimento['SubFamilia'].represent(r(f)))
            elif f == 'Stock':
                vals.append(r["_extra"]['SUM(LineaAlmacen.Stock)'])
            else:
                vals.append(r[f])

        rows.append(dict(id=r.CabeceraAlmacen.id, cell=vals))

    total = db(db.CabeceraAlmacen.alimento == db.Alimento.id).count()
    pages = math.ceil(1.0 * total / pagesize)
    data = dict(records=total, total=pages, page=page, rows=rows)

    return data


@service.json
def get_rows_entradas():
    """ this gets passed a few URL arguments: page number, and rows per page, and sort column, and sort desc or asc
    """

    fields = ['Donante', 'Fecha', 'tipoProcedencia']
    rows = []
    page = int(request.vars.page)  # the page number
    pagesize = int(request.vars.rows)

    limitby = (page * pagesize - pagesize, page * pagesize)
    orderby = ~db.CabeceraEntrada.Fecha
    #query = ""
    query = (db.CabeceraEntrada.id>0)
    if session.FechaAlmacen:
        query = query & (db.CabeceraEntrada.FechaAlmacen==session.FechaAlmacen)
    if session.DonanteAlmacen:
        query = query & (db.CabeceraEntrada.Donante==session.DonanteAlmacen)
    if session.ProcedenciaAlmacen:
        query = query & (db.CabeceraEntrada.tipoProcedencia== session.ProcedenciaAlmacen)
    if session.AlmacenAlimento:
        query = query & (db.CabeceraEntrada.id==db.LineaEntrada.cabecera)
        query = query & (db.LineaEntrada.alimento ==session.AlmacenAlimento)
    rowsentradas = db(query).select(db.CabeceraEntrada.ALL, limitby=limitby, orderby=orderby)
    print db._lastsql
    for r in rowsentradas:
        # print db._lastsql
        vals = []
        for f in fields:
            # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
            if f == 'Donante':
                # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
                vals.append(db.CabeceraEntrada['Donante'].represent(r(f)))
            else:
                vals.append(r[f])

        rows.append(dict(id=r.id, cell=vals))

    total = db(db.CabeceraEntrada.id > 0).count()
    pages = math.ceil(1.0 * total / pagesize)
    data = dict(records=total, total=pages, page=page, rows=rows)

    return data


@service.json
def get_lineas():

    fields = ['Stock', 'Caducidad', 'PesoUnidad', 'stockinicial', 'Lote']
    rows = []
    cabecera_id = request.vars.id
    query = (db.LineaAlmacen.cabecera == cabecera_id)
    for r in db(query).select(orderby=db.LineaAlmacen.Caducidad):
        vals = []
        for f in fields:
            if f == 'Caducidad':
                k = r(f).strftime('%d/%m/%Y')
                vals.append(k)
            else:
                vals.append(str(r[f]))
        rows.append(dict(id=r.id, cell=vals))
    return response.json(dict(rows=rows))


@service.json
def get_lineas_entradas():

    fields = ['alimento', 'Unidades', 'PesoUnidad', 'Caducidad', 'Lote']
    rows = []
    cabecera_id = request.vars.id
    query = (db.LineaEntrada.cabecera == cabecera_id)
    for r in db(query).select():
        vals = []
        for f in fields:
            if f == 'Caducidad':
                k = r(f).strftime('%d/%m/%Y')
                vals.append(k)
                print k
            elif f == 'alimento':
                k = db.LineaEntrada['alimento'].represent(r(f))
                vals.append(k)
            elif f == 'Lote':
                vals.append(r[f] or '')
            else:
                vals.append(str(r[f]))
        rows.append(dict(id=r.id, cell=vals))
    return response.json(dict(rows=rows))


@auth.requires_login()
def incidencias():

    return locals()


@service.json
def set_subfamilia():
    if len(request.vars) > 0:
        session.AlmacenSubFamilia = request.vars.subfamilia
        session.AlmacenAlimento = None

    return {}


@service.json
def set_parametros():
    if len(request.vars) > 0:
        parametro=request.vars.param
        valor = request.vars.objeto    
        if parametro == 'fecha':
            session.FechaAlmacen= valor
        elif parametro == 'donante':
            session.DonanteAlmacen= valor
        elif parametro == 'procedencia':
            session.ProcedenciaAlmacen = valor
    return {} 


def get_subfamilias():
    familia_id = request.vars.Familia
    session.AlmacenFamilia = familia_id
    session.AlmacenSubFamilia = None
    session.AlmacenAlimento = None
    rows = db(db.SubFamilia.Familia == familia_id).select(db.SubFamilia.ALL)
    optsf = [OPTION(row.Descripcion, _value=row.id) for row in rows]
    optsf.insert(0, OPTION(""))
    #import pdb;pdb.set_trace()
    subfamilias = XML("Subfamilia: ") + SELECT(
        optsf, _id="Alimento_SubFamilia", _name="SubFamilia", _class="generic-widget")

    return subfamilias


def get_alimentos():
    q = request.vars.term
    fam = ''
    subf = ''
    if request.vars.fam:
        fam = request.vars.fam
    if request.vars.subf:
        subf = request.vars.subf
    # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
    if q:
        search_term = q.lower().replace(" ", "-")
        query = (db.Alimento.Descripcion.contains(search_term))
        if fam != '':
            query = query & (db.Alimento.Familia == fam)
        if subf != '':
            query = query & (db.Alimento.SubFamilia == subf)
        rows = db(query).select(db.Alimento.Descripcion)
        return response.json([s['Descripcion'] for s in rows])

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
