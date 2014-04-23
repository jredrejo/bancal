# -*- coding: utf-8 -*-
import math
import locale
from datetime import datetime
if 0:
    from gluon import *

from gluon.storage import Storage
from plugin_suggest_widget import suggest_widget


@auth.requires_login()
def index():
    redirect(URL('entradas'))


@auth.requires_login()
def stock():

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
    db.CabeceraEntrada.Donante.widget = suggest_widget(
        db.Colaborador.name, id_field=db.Colaborador.id, min_length=1, limitby=(0, 50),
        keyword='_autocomplete_category_2_%(fieldname)s', user_signature=True)

    registro = None
    if session.current_entrada:
        registro = db.CabeceraEntrada(session.current_entrada)
        session.NuevaLinea = True
    form = SQLFORM(db.CabeceraEntrada, record=registro,
                   submit_button='Grabar estos datos', keepvalues=True)
    #import ipdb;ipdb.set_trace()
    if request.vars._autocomplete_Colaborador_name_aux:
        request.vars.pop('_autocomplete_Colaborador_name_aux')
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
        frmlineas = SQLFORM(db.LineaEntrada, registro_linea, _id="frmlineas",
                            submit_button='Guardar esta línea', keepvalues=False)
        if 'lid' in request.vars:
            frmlineas.vars.alimento = registro_alimento.Descripcion
        if "alimento" in request.vars:
            if session.AlmacenAlimento:
                request.vars.alimento = session.AlmacenAlimento
        # session.AlmacenAlimento
        if frmlineas.accepts(request.vars, session):
            session.NuevaLinea = True
            if valor_antiguo_uds and registro_linea.LineaAlmacen:
                actualiza_lineaalmacen(
                    registro_linea.LineaAlmacen, float(request.vars.Unidades), valor_antiguo_uds)
            else:
                cid = nueva_lineaalmacen(request.vars)
                registro_linea = db.LineaEntrada(frmlineas.vars.id)
                registro_linea.LineaAlmacen = cid
                registro_linea.update_record()

            redirect(URL(f="nueva_entrada", args=session.current_entrada))
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
    session.AlmacenStock = None
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
    db.CabeceraSalida.Beneficiario.widget = suggest_widget(
        db.Beneficiario.name, id_field=db.Beneficiario.id, min_length=1, limitby=(0, 50),
        keyword='_autocomplete_category_2_%(fieldname)s', user_signature=True)
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
        valor_antiguo_uds = 0
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
        db.LineaSalida.LineaAlmacen.writable = True
        frmlineas = SQLFORM(
            db.LineaSalida, registro_linea, submit_button='Guardar esta línea', _id="frmlineas")
        if 'lid' in request.vars:
            frmlineas.vars.alimento = registro_alimento.Descripcion
        if "alimento" in request.vars:
            if session.AlmacenAlimento:
                request.vars.alimento = session.AlmacenAlimento

        # session.AlmacenAlimento

        session.valor_antiguo = valor_antiguo_uds
        if frmlineas.accepts(request.vars, session, onvalidation=check_stock):
            session.NuevaLinea = True
            stock_pendiente = float(frmlineas.vars.Unidades)
            # descontamos el stock ahora de las líneas de almacén que haga
            # falta:
            query = (db.CabeceraAlmacen.alimento == frmlineas.vars.alimento) & (
                db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)
            lineas_almacen = db(query).select(
                db.LineaAlmacen.id, db.LineaAlmacen.Stock, orderby=~db.LineaAlmacen.Stock)
            if valor_antiguo_uds > 0:
                actualiza_lineaalmacen(
                    lineas_almacen.first().id, valor_antiguo_uds, stock_pendiente)
            else:
                for linea in lineas_almacen:
                    if stock_pendiente <= linea.Stock:
                        stock_resta = stock_pendiente
                        stock_pendiente = 0
                    else:
                        stock_resta = linea.Stock
                        stock_pendiente = stock_pendiente - stock_resta
                    actualiza_lineaalmacen(
                        linea.id, 0, stock_resta)
                    if stock_pendiente == 0:
                        break

            redirect(URL(f="nueva_salida", args=session.current_entrada))
        elif frmlineas.errors:
            response.flash = 'Error en los datos'
    response.files.append(
        URL(r=request, c='static/jqGrid/js/i18n', f='grid.locale-es.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/js', f='jquery.jqGrid.min.js'))
    response.files.append(
        URL(r=request, c='static/jqGrid/css', f='ui.jqgrid.css'))

    return dict(form=form, frmlineas=frmlineas, codigo_alimento=codigo_alimento)


def check_stock(form):
    stock_pendiente = float(form.vars.Unidades)
    query = (db.CabeceraAlmacen.alimento == form.vars.alimento) & (
        db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)
    stock_actual = db(query).select(
        db.LineaAlmacen.Stock.sum()).first()[db.LineaAlmacen.Stock.sum()]
    if stock_pendiente - session.valor_antiguo > stock_actual:
        stock_pendiente = stock_actual + session.valor_antiguo
        form.vars.Unidades = stock_pendiente


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
        if session.Entradas:
            actualiza_lineaalmacen(linea.id, float(valores.Unidades), 0)
        lid = linea.id
    else:
        lid = db.LineaAlmacen.insert(
            cabecera=cid, PesoUnidad=valores.PesoUnidad,
            Caducidad=fecha_caducidad, estanteria=valores.estanteria,
            Lote=valores.Lote, Stock=float(valores.Unidades))
    return lid


@service.json
def get_codigo():
    codigo = request.vars.codigo
    alimento = db((db.Alimento.Codigo == codigo) & (db.Alimento.Descripcion!=None) ).select().first()
    if alimento:
        data = {"alimento": alimento.Descripcion}
        session.AlmacenAlimento = alimento.id

        if not session.Entradas:
            query = (db.CabeceraAlmacen.alimento == db.Alimento.id) & (
                db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)
            query = query & (db.Alimento.id == alimento.id)
            stock = db(query).select(db.LineaAlmacen.Stock.sum()).first()[
                db.LineaAlmacen.Stock.sum()]

            if stock:
                locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')
                session.AlmacenStock = stock
                data["stock"] = stock
                data[
                    "stock-text"] = locale.format("%.2f", stock, grouping=True)
            else:
                data = {"alimento": ''}
                session.AlmacenAlimento = None
                session.AlmacenStock = None

    else:
        data = {"alimento": ''}
        session.AlmacenAlimento = None

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

    if not session.Entradas:
        data = {"codigo": codigo, "stock": 0, "stock-text": ''}
        locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')
        if codigo != '':
            query = (db.CabeceraAlmacen.alimento == db.Alimento.id) & (
                db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)
            query = query & (db.Alimento.Codigo == codigo)
            stock = db(query).select(db.LineaAlmacen.Stock.sum()).first()[
                db.LineaAlmacen.Stock.sum()]
            if stock:
                session.AlmacenStock = stock
                data["stock"] = stock
                data[
                    "stock-text"] = locale.format("%.2f", stock, grouping=True)
            else:
                session.AlmacenStock = None
                data["stock"] = 0
                data["stock-text"] = ""
        return response.json(data)
    else:
        return response.json(codigo)


@auth.requires_login()
@service.json
def get_rows():
    fields = ['Alimento.Codigo', 'Alimento.Descripcion',
              'Alimento.Conservacion', 'Stock', 'Alimento.Unidades']
    rows = []
    page = int(request.vars.page)  # the page number
    pagesize = int(request.vars.rows)

    limitby = (page * pagesize - pagesize, page * pagesize)

    if request.vars.sidx == 'Stock':
        orderby = db.LineaAlmacen.Stock.sum()
    elif request.vars.sidx == "kkkkk":
        orderby = ~db.LineaAlmacen.id
    else:
        orderby = db.Alimento[request.vars.sidx]
    if request.vars.sord == 'desc':
        orderby = ~orderby
    query = (db.CabeceraAlmacen.alimento == db.Alimento.id) & (
        db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera) & (db.Alimento.Descripcion!=None)

    if session.AlmacenAlimento:
        query = query & (db.Alimento.id == session.AlmacenAlimento)
    for r in db(
        query).select(db.CabeceraAlmacen.id, db.Alimento.Codigo, db.Alimento.Descripcion, db.Alimento.Conservacion, db.Alimento.Unidades, db.LineaAlmacen.Stock.sum(
    ),
            limitby=limitby, orderby=orderby, groupby=db.CabeceraAlmacen.alimento):
        # print db._lastsql
        vals = []
        for f in fields:
            if f == 'Stock':
                vals.append(r["_extra"]['SUM(LineaAlmacen.Stock)'])
            else:
                vals.append(r[f])

        rows.append(dict(id=r.CabeceraAlmacen.id, cell=vals))
    # print db._lastsql
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
    fields = ['nada', 'Beneficiario', 'Fecha']
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
    fields = ['alimento', 'Unidades', 'PesoUnidad', 'Caducidad']
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
            fields = ["nada", ] + fields

    if session.Entradas:
        query = (db.LineaEntrada.cabecera == cabecera_id)
        suma = db.LineaEntrada.Unidades.sum()
        ordenacion = ~db.LineaEntrada.id
    else:
        query = (db.LineaSalida.cabecera == cabecera_id)
        suma = db.LineaSalida.Unidades.sum()
        ordenacion = ~db.LineaSalida.id

    totales = db(query).select(suma)
    qty_totales = totales.first()[suma]
    locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')
    for r in db(query).select(limitby=limitby, orderby=ordenacion):
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
                vals.append(locale.format("%.2f", r[f], grouping=True))
        rows.append(dict(id=r.id, cell=vals))

    if EnDetalle:
        if qty_totales:
            totales = locale.format("%.2f", qty_totales, grouping=True)
        else:
            totales = ""
        total = db(query).count()
        pages = math.ceil(1.0 * total / pagesize)
        data = dict(records=total, total=pages, page=page,
                    rows=rows, userdata={'qty_totales': totales})
        return data
    else:
        return response.json(dict(rows=rows))


@auth.requires_login()
@service.json
def get_lineas_almacen():
    fields = ['alimento', 'Stock', 'PesoUnidad',
              'Caducidad', 'Lote', 'estanteria', 'Palets']
    rows = []
    limitby = None
    total = 0
    pages = 0
    page = int(request.vars.page)  # the page number
    pagesize = int(request.vars.rows)
    limitby = (page * pagesize - pagesize, page * pagesize)
    cabecera = db(
        db.CabeceraAlmacen.alimento == session.AlmacenAlimento).select().first()
    if cabecera:
        query = (db.LineaAlmacen.cabecera == cabecera.id) & (
            db.LineaAlmacen.Stock > 0)
        mialimento = db.CabeceraAlmacen[
            'alimento'].represent(cabecera.alimento)
        for r in db(query).select(limitby=limitby):
            vals = []
            for f in fields:
                if f == 'Caducidad':
                    if r(f):
                        k = r(f).strftime('%d/%m/%Y')
                    else:
                        k = ""
                    vals.append(k)
                elif f == 'alimento':
                    vals.append(mialimento)
                elif f == 'Lote':
                    vals.append(r[f] or '')
                else:
                    vals.append(str(r[f]))
            rows.append(dict(id=r.id, cell=vals))
            total = db(query).count()
            pages = math.ceil(1.0 * total / pagesize)
    data = dict(records=total, total=pages, page=page, rows=rows)
    return data


@auth.requires_login()
def incidencias():
    return locals()


@auth.requires_login()
@service.json
def borra_linea():
    if 'linea_id' in request.vars:
        borrar_linea(request.vars.linea_id)


def borrar_linea(linea_id=None):
    if linea_id:
        if session.Entradas:
            registro = db.LineaEntrada(linea_id)
            if registro.LineaAlmacen > 0:
                actualiza_lineaalmacen(
                    registro.LineaAlmacen, 0, registro.Unidades)
            db(db.LineaEntrada.id == linea_id).delete()
        else:
            registro = db.LineaSalida(linea_id)
            cabecera = db(
                db.CabeceraAlmacen.alimento == registro.alimento).select().first()
            query = (db.LineaAlmacen.cabecera == cabecera.id)
            linea_almacen = db(query).select(
                db.LineaAlmacen.id, orderby=~db.LineaAlmacen.Stock).first()
            # metemos el stock de la línea borrada en la lína
            # de stock que más tenga. No se lleva registro de las
            # líneas de almacén que hubiera antes:
            if linea_almacen > 0:
                actualiza_lineaalmacen(
                    linea_almacen.id, registro.Unidades, 0)
            db(db.LineaSalida.id == linea_id).delete()


@auth.requires_login()
@service.json
def borra_entrada():
    if 'entrada_id' in request.vars:
        query = (db.LineaEntrada.cabecera == db.CabeceraEntrada.id) & (
            db.CabeceraEntrada.id == request.vars.entrada_id)
        rows = db(query).select(db.LineaEntrada.id)
        for row in rows:
            borrar_linea(row.id)

        db(db.CabeceraEntrada.id == request.vars.entrada_id).delete()


@auth.requires_login()
@service.json
def borra_salida():
    if 'salida_id' in request.vars:
        query = (db.LineaSalida.cabecera == db.CabeceraSalida.id) & (
            db.CabeceraSalida.id == request.vars.salida_id)
        rows = db(query).select(db.LineaSalida.id)
        for row in rows:
            borrar_linea(row.id)
        db(db.CabeceraSalida.id == request.vars.salida_id).delete()


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


def get_alimentos():
    q = request.vars.term
    if q:
        search_term = q.lower().replace(" ", "-")
        query = (db.Alimento.Descripcion.contains(search_term))

        rows = db(query).select(db.Alimento.Descripcion)
        return response.json([s['Descripcion'] for s in rows])

    return ''


def get_donante():
    q = request.vars.term
    if q:
        query = (db.Colaborador.name.contains(q)) & (
            db.Colaborador.Donante == True)
        rows = db(query).select(db.Colaborador.name)
        return response.json([s['name'] for s in rows])

    return ''


def set_donante():

    q = request.vars.donante
    if q:
        query = (db.Colaborador.name == q) & (db.Colaborador.Donante == True)
        row = db(query).select(db.Colaborador.name, db.Colaborador.id).first()
        data = {"donante": row.id}
        data = row.id
        return data
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
