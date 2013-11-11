# -*- coding: utf-8 -*-
import math
from datetime import datetime
if 0:
    from gluon import *


@auth.requires_login()
def index():
    redirect(URL('entradas'))


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
    session.Entradas = True
    session.FechaAlmacen = None
    session.DonanteAlmacen = None
    session.ProcedenciaAlmacen = None
    session.AlmacenAlimento = None
    db.Alimento.Descripcion.widget = ajax_autocomplete
    form = SQLFORM(db.CabeceraEntrada)

    response.files.append(
        URL(r=request, c='static/jqGrid/js/i18n', f='grid.locale-es.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/js', f='jquery.jqGrid.min.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/css', f='ui.jqgrid.css'))

    return locals()


@auth.requires_login()
def salidas():
    session.Entradas = None
    session.FechaAlmacen = None
    session.BeneficiarioAlmacen = None
    session.AlmacenAlimento = None
    db.Alimento.Descripcion.widget = ajax_autocomplete
    form = SQLFORM(db.CabeceraSalida)

    # if request.vars.Descripcion:
    #    session.AlmacenAlimento=request.vars.Descripcion
    response.files.append(
        URL(r=request, c='static/jqGrid/js/i18n', f='grid.locale-es.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/js', f='jquery.jqGrid.min.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/css', f='ui.jqgrid.css'))

    return locals()


@auth.requires_login()
def nueva_entrada():
    session.Entradas = True
    session.NuevaLinea = None
    frmlineas = None
    codigo_alimento = None
    if len(request.args) > 0:
        session.current_entrada = request.args[0]
    else:
        session.current_entrada = None
    db.CabeceraEntrada.almacen.writable = False
    db.CabeceraEntrada.almacen.readable = False
    registro = None
    if session.current_entrada:
        registro = db.CabeceraEntrada(session.current_entrada)
        session.NuevaLinea = True
    form = SQLFORM(db.CabeceraEntrada, record=registro,
                   submit_button='Grabar estos datos', keepvalues=True)
    if form.accepts(request.vars, session):
        response.flash = 'Nueva entrada grabada'
        session.current_entrada = form.vars.id
        redirect(URL('nueva_entrada', args=[form.vars.id]))
    elif form.errors:
        response.flash = 'Error en los datos'

    if session.current_entrada:
        valor_antiguo_uds = None
        if 'lid' in request.vars:
            registro_linea = db.LineaEntrada(request.vars.lid)
            registro_alimento = db.Alimento(registro_linea.alimento)
            codigo_alimento = registro_alimento.Codigo
            session.AlmacenAlimento = registro_alimento.id
            session.NuevaLinea = True
            if request.vars.Unidades:
                if float(request.vars.Unidades) != registro_linea.Unidades:
                    valor_antiguo_uds = registro_linea.Unidades
        else:
            registro_linea = None
            codigo_alimento = XML('""')
        db.LineaEntrada.cabecera.default = session.current_entrada
        frmlineas = SQLFORM(
            db.LineaEntrada, registro_linea, submit_button='Guardar esta línea')
        if 'lid' in request.vars:
            frmlineas.vars.alimento = registro_alimento.Descripcion
        if "alimento" in request.vars:
            if session.AlmacenAlimento:
                request.vars.alimento = session.AlmacenAlimento
        # session.AlmacenAlimento
        if frmlineas.accepts(request.vars, session):
            # PENDIENTE: METER ESTOS DATOS EN LAS LINEASALMACEN
            session.NuevaLinea = True
            if valor_antiguo_uds:
                actualiza_lineaalmacen(
                    registro_linea.LineaAlmacen, float(request.vars.Unidades), valor_antiguo_uds)
            else:
                nueva_lineaalmacen(request.vars)
        elif frmlineas.errors:
            response.flash = 'Error en los datos'
    response.files.append(
        URL(r=request, c='static/jqGrid/js/i18n', f='grid.locale-es.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/js', f='jquery.jqGrid.min.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/css', f='ui.jqgrid.css'))

    return dict(form=form, frmlineas=frmlineas, codigo_alimento=codigo_alimento)


@auth.requires_login()
def nueva_salida():
    session.Entradas = False
    session.NuevaLinea = None
    frmlineas = None
    codigo_alimento = None    
    if len(request.args) > 0:
        # uso session.current_entrada en lugar de session.current_salida para
        # que valga la misma función de  get_lineas_entradas en entradas y
        # salidas
        session.current_entrada = request.args[0]
    else:
        session.current_entrada = None
    db.CabeceraSalida.almacen.writable = False
    db.CabeceraSalida.almacen.readable = False
    registro = None
    if session.current_entrada:
        registro = db.CabeceraSalida(session.current_entrada)
        session.NuevaLinea = True
    form = SQLFORM(db.CabeceraSalida, record=registro,
                   submit_button='Grabar estos datos', keepvalues=True)
    if form.accepts(request.vars, session):
        response.flash = 'Nueva salida grabada'
        session.current_entrada = form.vars.id
        redirect(URL('nueva_salida', args=[form.vars.id]))
    elif form.errors:
        response.flash = 'Error en los datos'

    if session.current_entrada:
        valor_antiguo_uds = None
        if 'lid' in request.vars:
            registro_linea = db.LineaSalida(request.vars.lid)
            registro_alimento = db.Alimento(registro_linea.alimento)
            codigo_alimento = registro_alimento.Codigo
            session.AlmacenAlimento = registro_alimento.id
            session.NuevaLinea = True
            if request.vars.Unidades:
                if float(request.vars.Unidades) != registro_linea.Unidades:
                    valor_antiguo_uds = registro_linea.Unidades
        else:
            registro_linea = None
            codigo_alimento = XML('""')
        db.LineaSalida.cabecera.default = session.current_entrada
        frmlineas = SQLFORM(
            db.LineaSalida, registro_linea, submit_button='Guardar esta línea')
        if 'lid' in request.vars:
            frmlineas.vars.alimento = registro_alimento.Descripcion
        if "alimento" in request.vars:
            if session.AlmacenAlimento:
                request.vars.alimento = session.AlmacenAlimento
        # session.AlmacenAlimento
        if frmlineas.accepts(request.vars, session):
            # PENDIENTE: METER ESTOS DATOS EN LAS LINEASALMACEN
            session.NuevaLinea = True
            if valor_antiguo_uds:
                actualiza_lineaalmacen(
                    registro_linea.LineaAlmacen, valor_antiguo_uds,float(request.vars.Unidades))
            else:
                nueva_lineaalmacen(request.vars)
        elif frmlineas.errors:
            response.flash = 'Error en los datos'
    response.files.append(
        URL(r=request, c='static/jqGrid/js/i18n', f='grid.locale-es.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/js', f='jquery.jqGrid.min.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/css', f='ui.jqgrid.css'))

    return dict(form=form, frmlineas=frmlineas, codigo_alimento=codigo_alimento)


def actualiza_lineaalmacen(linea, valornuevo, valorprevio=None):
    registro = db.LineaAlmacen(linea)
    total = float(registro.Stock)
    registro.Stock = total + (valornuevo - valorprevio)
    registro.update_record()


def nueva_lineaalmacen(valores):
    cabecera = db(
        db.CabeceraAlmacen.alimento == valores.alimento).select().first()
    if not cabecera:
        cid = db.CabeceraAlmacen.insert(alimento=valores.alimento)
    else:
        cid = cabecera.id
    fecha_caducidad = datetime.strptime(valores.Caducidad, '%d-%m-%Y')
    query = (db.LineaAlmacen.cabecera == cid) & (
        db.LineaAlmacen.PesoUnidad == valores.PesoUnidad)
    query = query & (db.LineaAlmacen.Caducidad == fecha_caducidad)
    query = query & (db.LineaAlmacen.estanteria == valores.estanteria)
    query = query & (db.LineaAlmacen.Lote == valores.Lote)
    linea = db(query).select().first()
    if linea:
        actualiza_lineaalmacen(linea.id, float(valores.Unidades), 0)
    else:
        db.LineaAlmacen.insert(cabecera=cid, PesoUnidad=valores.PesoUnidad,
                               Caducidad=fecha_caducidad, estanteria=valores.estanteria,
                               Lote=valores.Lote, Stock=float(valores.Unidades))


@service.json
def get_codigo():
    codigo = request.vars.codigo
    alimento = db(db.Alimento.Codigo == codigo).select().first()
    if alimento:
        data = {"alimento": alimento.Descripcion}
        session.AlmacenAlimento = alimento.id
    else:
        data = {"alimento": ''}
    return response.json(data)


@service.json
def set_alimento():
    codigo = ''
    if len(request.vars) > 0:
        session.AlmacenAlimento = request.vars.alimento
        alimento = db(
            db.Alimento.Descripcion == request.vars.alimento).select().first()
        if alimento:
            codigo = alimento.Codigo
            session.AlmacenAlimento = alimento.id
    if codigo == '':
        session.AlmacenAlimento = None
    return response.json(codigo)


@auth.requires_login()
@service.json
def get_rows():
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


@auth.requires_login()
@service.json
def get_rows_entradas():
    fields = ['nada', 'Donante', 'Fecha', 'tipoProcedencia']
    rows = []
    page = int(request.vars.page)  # the page number
    pagesize = int(request.vars.rows)

    limitby = (page * pagesize - pagesize, page * pagesize)

    if request.vars.sidx == 'Procedencia':
        orderby = db.CabeceraEntrada.tipoProcedencia
    elif request.vars.sidx == 'Donante':
        orderby = db.CabeceraEntrada.Donante
    elif request.vars.sidx == 'Fecha':
        orderby = db.CabeceraEntrada.Fecha
    else:
        orderby = ~db.CabeceraEntrada.Fecha
    if request.vars.sord == 'desc':
        orderby = ~orderby

    query = (db.CabeceraEntrada.id > 0)
    if session.FechaAlmacen:
        query = query & (db.CabeceraEntrada.Fecha == session.FechaAlmacen)
    if session.DonanteAlmacen:
        query = query & (db.CabeceraEntrada.Donante == session.DonanteAlmacen)
    if session.ProcedenciaAlmacen:
        query = query & (
            db.CabeceraEntrada.tipoProcedencia == session.ProcedenciaAlmacen)
    if session.AlmacenAlimento:
        query = query & (db.CabeceraEntrada.id == db.LineaEntrada.cabecera)
        query = query & (db.LineaEntrada.alimento == session.AlmacenAlimento)
    rowsentradas = db(query).select(
        db.CabeceraEntrada.ALL, limitby=limitby, orderby=orderby)
    # print db._lastsql
    for r in rowsentradas:
        # print db._lastsql
        vals = []
        for f in fields:
            if f == 'nada':
                vals.append("")
            elif f == 'Donante':
                # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
                vals.append(db.CabeceraEntrada['Donante'].represent(r(f)))
            else:
                vals.append(r[f])

        rows.append(dict(id=r.id, cell=vals))

    total = db(db.CabeceraEntrada.id > 0).count()
    pages = math.ceil(1.0 * total / pagesize)
    data = dict(records=total, total=pages, page=page, rows=rows)

    return data


@auth.requires_login()
@service.json
def get_rows_salidas():
    fields = ['nada','Beneficiario', 'Fecha']
    rows = []
    page = int(request.vars.page)  # the page number
    pagesize = int(request.vars.rows)

    limitby = (page * pagesize - pagesize, page * pagesize)
    if request.vars.sidx == 'Beneficiario':
        orderby = db.CabeceraSalida.Beneficiario
    elif request.vars.sidx == 'Fecha':
        orderby = db.CabeceraSalida.Fecha
    else:
        orderby = ~db.CabeceraSalida.Fecha
    if request.vars.sord == 'desc':
        orderby = ~orderby
    #query = ""
    query = (db.CabeceraSalida.id > 0)
    if session.FechaAlmacen:
        query = query & (db.CabeceraSalida.Fecha == session.FechaAlmacen)
    if session.BeneficiarioAlmacen:
        query = query & (
            db.CabeceraSalida.Beneficiario == session.BeneficiarioAlmacen)
    if session.AlmacenAlimento:
        query = query & (db.CabeceraSalida.id == db.LineaSalida.cabecera)
        query = query & (db.LineaSalida.alimento == session.AlmacenAlimento)
    rowssalidas = db(query).select(
        db.CabeceraSalida.ALL, limitby=limitby, orderby=orderby)

    for r in rowssalidas:
        # print db._lastsql
        vals = []
        for f in fields:
            if f == 'nada':
                vals.append("")            
            elif f == 'Beneficiario':
                # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
                vals.append(db.CabeceraSalida['Beneficiario'].represent(r(f)))
            else:
                vals.append(r[f])

        rows.append(dict(id=r.id, cell=vals))

    total = db(db.CabeceraSalida.id > 0).count()
    pages = math.ceil(1.0 * total / pagesize)
    data = dict(records=total, total=pages, page=page, rows=rows)

    return data


@auth.requires_login()
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


@auth.requires_login()
@service.json
def get_lineas_entradas():

    fields = ['alimento', 'Unidades', 'PesoUnidad', 'Caducidad', 'Lote']
    rows = []
    EnDetalle = False
    limitby = None
    if 'id' in request.vars:
        cabecera_id = request.vars.id
    elif "current_entrada" in session.keys():
        if session.current_entrada:
            cabecera_id = session.current_entrada
            page = int(request.vars.page)  # the page number
            pagesize = int(request.vars.rows)
            limitby = (page * pagesize - pagesize, page * pagesize)
            EnDetalle = True
            fields = ["nada", ] + fields + ["estanteria", ]

    if session.Entradas:
        query = (db.LineaEntrada.cabecera == cabecera_id)
    else:
        query = (db.LineaSalida.cabecera == cabecera_id)
    for r in db(query).select(limitby=limitby):
        vals = []
        for f in fields:
            if f == 'nada':
                vals.append("")
            elif f == 'Caducidad':
                k = r(f).strftime('%d/%m/%Y')
                vals.append(k)
            elif f == 'alimento':
                k = db.LineaEntrada['alimento'].represent(r(f))
                vals.append(k)
            elif f == 'Lote':
                vals.append(r[f] or '')
            else:
                vals.append(str(r[f]))
        rows.append(dict(id=r.id, cell=vals))

    if EnDetalle:
        total = db(query).count()
        pages = math.ceil(1.0 * total / pagesize)
        data = dict(records=total, total=pages, page=page, rows=rows)
        return data
    else:
        return response.json(dict(rows=rows))


@auth.requires_login()
def incidencias():
    return locals()


@auth.requires_login()
@service.json
def borra_linea():
    if 'linea_id' in request.vars:
        if session.Entradas:
            registro = db.LineaEntrada(request.vars.linea_id)
            if registro.LineaAlmacen > 0:
                actualiza_lineaalmacen(registro.LineaAlmacen, 0, registro.Unidades)
            db(db.LineaEntrada.id == request.vars.linea_id).delete()
        else:
            registro = db.LineaSalida(request.vars.linea_id)
            if registro.LineaAlmacen > 0:
                actualiza_lineaalmacen(registro.LineaAlmacen, registro.Unidades,0)
            db(db.LineaSalida.id == request.vars.linea_id).delete()            

@auth.requires_login()
@service.json
def borra_entrada():
    if 'entrada_id' in request.vars:
        registro = db.CabeceraEntrada(request.vars.entrada_id)
        rows = db(db.LineaEntrada.cabecera==registro.id).select()
        for row in rows:        
            if row.LineaAlmacen > 0:
                actualiza_lineaalmacen(row.LineaAlmacen, 0, row.Unidades)
            db(db.LineaEntrada.id == row.id).delete()
        db(db.CabeceraEntrada.id==request.vars.entrada_id).delete()

@auth.requires_login()
@service.json
def borra_salida():
    if 'salida_id' in request.vars:
        registro = db.CabeceraSalida(request.vars.salida_id)
        rows = db(db.LineaSalida.cabecera==registro.id).select()
        for row in rows:        
            if row.LineaAlmacen > 0:
                actualiza_lineaalmacen(row.LineaAlmacen,row.Unidades,0)
            db(db.LineaSalida.id == row.id).delete()
        db(db.CabeceraSalida.id==request.vars.salida_id).delete()

@service.json
def set_subfamilia():
    if len(request.vars) > 0:
        session.AlmacenSubFamilia = request.vars.subfamilia
        session.AlmacenAlimento = None

    return {}


@auth.requires_login()
@service.json
def set_parametros():
    if len(request.vars) > 0:
        parametro = request.vars.param
        valor = request.vars.objeto
        if valor == '':
            valor = None
        if parametro == 'fecha':
            if valor:
                session.FechaAlmacen = datetime.date(
                    datetime.strptime(valor, '%d-%m-%Y'))
            else:
                session.FechaAlmacen = None
        elif parametro == 'donante':
            session.DonanteAlmacen = valor
        elif parametro == 'beneficiario':
            session.BeneficiarioAlmacen = valor
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
    return response.download(request, db)


def call():
    return service()


@auth.requires_signature()
def data():
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
