#!/usr/bin/python
# -*- coding: utf-8 -*-

##############################################################################
# Project:     Bancal - Gestión de almacén para los Bancos de Alimentos
# Language:    Python 2.7
# Date:        15-Ago-2013.
# Ver.:        20-Jul-2016.
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

################################################
# Variables de sesión usadas:
#
# session.AlmacenAlimento: almacena el id de db.Alimento.id del alimento que se está editando, también usado para búsquedas
# session.Entradas = True si se está gestionando entradas, False si son salidas. Usado por get_lineas_entradas
# session.FechaAlmacen: Usada para hacer búsquedas en esa fecha
# session.DonanteAlmacen = Usada para hacer búsquedas con ese donante
# session.BeneficiarioAlmacen: Usada para hacer búsquedas sobre ese beneficiario
# session.ProcedenciaAlmacen = Usada para hacer búsquedas sobre esa procedencia
# session.current_entrada = db.CabeceraEntrada.id  o db.CabeceraSalida.id de la entrada o salida que se está editando


import math
import locale
from datetime import datetime
from gluon import current

from plugin_suggest_widget import suggest_widget
from movimientos import *

if 0:  # for IDE's to find the imports for the globals
    from gluon import *
    (request, session, response, T, cache) = (current.request,
                                              current.session, current.response, current.t, current.cache)
    LOAD = compileapp.LoadFactory()
    from gluon.sqlhtml import *
    from gluon.validators import *


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

    response.files.append(URL(r=request, c='static/jqGrid/js/i18n',
                              f='grid.locale-es.js'))
    response.files.append(URL(r=request, c='static/jqGrid/js',
                              f='jquery.jqGrid.min.js'))
    response.files.append(URL(r=request, c='static/jqGrid/css',
                              f='ui.jqgrid.css'))

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

    response.files.append(URL(r=request, c='static/jqGrid/js/i18n',
                              f='grid.locale-es.js'))
    response.files.append(URL(r=request, c='static/jqGrid/js',
                              f='jquery.jqGrid.min.js'))
    response.files.append(URL(r=request, c='static/jqGrid/css',
                              f='ui.jqgrid.css'))

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

    response.files.append(URL(r=request, c='static/jqGrid/js/i18n',
                              f='grid.locale-es.js'))
    response.files.append(URL(r=request, c='static/jqGrid/js',
                              f='jquery.jqGrid.min.js'))
    response.files.append(URL(r=request, c='static/jqGrid/css',
                              f='ui.jqgrid.css'))

    return locals()


@auth.requires_login()
def nueva_entrada():
    session.Entradas = True
    frmlineas = None
    codigo_alimento = None
    if len(request.args) > 0:
        session.current_entrada = request.args[0]
    else:
        session.current_entrada = None
    db.CabeceraEntrada.almacen.writable = False
    db.CabeceraEntrada.almacen.readable = False
    db.CabeceraEntrada.Donante.widget = suggest_widget(
        db.Colaborador.name,
        id_field=db.Colaborador.id,
        min_length=1,
        limitby=(0, 50),
        keyword='_autocomplete_category_2_%(fieldname)s',
        user_signature=True,
    )

    registro = None
    if session.current_entrada:
        registro = db.CabeceraEntrada(session.current_entrada)
    form = SQLFORM(db.CabeceraEntrada, record=registro,
                   submit_button='Grabar estos datos', keepvalues=True)

    if request.vars._autocomplete_Colaborador_name_aux:
        request.vars.pop('_autocomplete_Colaborador_name_aux')
    if form.accepts(request.vars, session, onvalidation=ver_cierre):
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
            if request.vars.Unidades:
                if float(request.vars.Unidades) \
                        != registro_linea.Unidades:
                    valor_antiguo_uds = registro_linea.Unidades
        else:
            registro_linea = None
            codigo_alimento = XML('""')
        db.LineaEntrada.cabecera.default = session.current_entrada
        frmlineas = SQLFORM(db.LineaEntrada, registro_linea,
                            _id='frmlineas',
                            submit_button='Guardar esta línea',
                            keepvalues=False)
        if 'lid' in request.vars:
            frmlineas.vars.alimento = registro_alimento.Descripcion
        if 'alimento' in request.vars:
            if session.AlmacenAlimento:
                request.vars.alimento = session.AlmacenAlimento

        # session.AlmacenAlimento
        if frmlineas.accepts(request.vars, session):
            if valor_antiguo_uds and registro_linea.LineaAlmacen:
                actualiza_lineaalmacen(registro_linea.LineaAlmacen,
                                       float(request.vars.Unidades), valor_antiguo_uds)
            else:
                cid = nueva_lineaalmacen(request.vars)
                registro_linea = db.LineaEntrada(frmlineas.vars.id)
                registro_linea.LineaAlmacen = cid
                registro_linea.update_record()

            redirect(URL(f='nueva_entrada',
                         args=session.current_entrada))
        elif frmlineas.errors:
            response.flash = 'Error en los datos'
    response.files.append(URL(r=request, c='static/jqGrid/js/i18n',
                              f='grid.locale-es.js'))
    response.files.append(URL(r=request, c='static/jqGrid/js',
                              f='jquery.jqGrid.min.js'))
    response.files.append(URL(r=request, c='static/jqGrid/css',
                              f='ui.jqgrid.css'))

    return dict(form=form, frmlineas=frmlineas,
                codigo_alimento=codigo_alimento)


@auth.requires_login()
def nueva_salida():
    session.Entradas = False
    session.AlmacenStock = None
    frmlineas = None
    codigo_alimento = None
    if len(request.args) > 0:

        # uso session.current_entrada en lugar de session.current_salida para.
        # que valga la misma función de  get_lineas_entradas en entradas y
        # salidas

        session.current_entrada = request.args[0]
    else:
        session.current_entrada = None
    db.CabeceraSalida.almacen.writable = False
    db.CabeceraSalida.almacen.readable = False
    db.CabeceraSalida.Beneficiario.widget = suggest_widget(
        db.Beneficiario.name,
        id_field=db.Beneficiario.id,
        min_length=1,
        limitby=(0, 50),
        keyword='_autocomplete_category_2_%(fieldname)s',
        user_signature=True,
    )
    registro = None
    if session.current_entrada:
        registro = db.CabeceraSalida(session.current_entrada)
    form = SQLFORM(db.CabeceraSalida, record=registro,
                   submit_button='Grabar estos datos', keepvalues=True)
    if form.accepts(request.vars, session, onvalidation=ver_cierre):
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
            if request.vars.Unidades:
                if float(request.vars.Unidades) \
                        != registro_linea.Unidades:
                    valor_antiguo_uds = registro_linea.Unidades
        else:
            registro_linea = None
            codigo_alimento = XML('""')
        db.LineaSalida.cabecera.default = session.current_entrada
        db.LineaSalida.LineaAlmacen.writable = True
        frmlineas = SQLFORM(db.LineaSalida, registro_linea,
                            submit_button='Guardar esta línea',
                            _id='frmlineas')
        if 'lid' in request.vars:
            frmlineas.vars.alimento = registro_alimento.Descripcion
        if 'alimento' in request.vars:
            if session.AlmacenAlimento:
                request.vars.alimento = session.AlmacenAlimento

        # session.AlmacenAlimento

        session.valor_antiguo = valor_antiguo_uds

        if frmlineas.accepts(request.vars, session,
                             onvalidation=check_stock):
            stock_pendiente = float(frmlineas.vars.Unidades)

            # descontamos el stock ahora de las líneas de almacén que haga
            # falta:
            query = (db.CabeceraAlmacen.alimento == frmlineas.vars.alimento) \
                & (db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)
            lineas_almacen = db(query).select(db.LineaAlmacen.id,
                                              db.LineaAlmacen.Stock,
                                              orderby=~db.LineaAlmacen.Stock)
            if valor_antiguo_uds > 0:
                actualiza_lineaalmacen(lineas_almacen.first().id,
                                       valor_antiguo_uds, stock_pendiente)
            else:
                for linea in lineas_almacen:
                    if stock_pendiente <= linea.Stock:
                        stock_resta = stock_pendiente
                        stock_pendiente = 0
                    else:
                        stock_resta = linea.Stock
                        if linea.Stock > 0:  # no restamos a un stock negativo
                            stock_pendiente = stock_pendiente - stock_resta
                        else:
                            stock_resta = 0
                    if stock_resta > 0:
                        actualiza_lineaalmacen(linea.id, 0, stock_resta)
                    # if stock_pendiente == 0:
                    #     break
                if stock_pendiente > 0:  # Va a haber stock negativo en el almacén, se lo asigno a la última línea
                    actualiza_lineaalmacen(linea.id, 0, stock_pendiente)

            redirect(URL(f='nueva_salida',
                         args=session.current_entrada))
        elif frmlineas.errors:
            response.flash = 'Error en los datos'
    response.files.append(URL(r=request, c='static/jqGrid/js/i18n',
                              f='grid.locale-es.js'))
    response.files.append(URL(r=request, c='static/jqGrid/js',
                              f='jquery.jqGrid.min.js'))
    response.files.append(URL(r=request, c='static/jqGrid/css',
                              f='ui.jqgrid.css'))

    return dict(form=form, frmlineas=frmlineas,
                codigo_alimento=codigo_alimento)


@service.json
def get_alimento_info():
    """Devuelve:
    - el código de un alimento dado su texto
    - Si hay stock devuelve también:
        - el stock disponible como número real
        - el stock disponible como cadena de texto"""
    codigo = ''
    if len(request.vars) > 0:
        if 'codigo' in request.vars:
            codigo = request.vars.codigo
        else:
            alimento = db(db.Alimento.Descripcion == request.vars.alimento).select().first()
            if alimento:
                codigo = alimento.Codigo

    data = stock_alimento(codigo, db)
    session.AlmacenStock = data['stock'] if data['stock'] else None
    session.AlmacenAlimento = data['id'] if data['id'] else None

    return response.json(data)


@auth.requires_login()
@service.json
def get_rows():
    """ Devuelve las filas del almacén con sus cantidades por alimento """
    fields = ['Alimento.Codigo', 'Alimento.Descripcion',
              'Alimento.Conservacion', 'Stock', 'Alimento.Unidades']
    rows = []
    try:
        page = int(request.vars.page)  # the page number
    except:
        page = 1
    try:
        pagesize = int(request.vars.rows)
    except:
        pagesize = 100

    limitby = (page * pagesize - pagesize, page * pagesize)

    # grid sorting:
    if request.vars.sidx == 'Stock':
        orderby = db.LineaAlmacen.Stock.sum()
    elif request.vars.sidx == 'kkkkk':
        orderby = db.Alimento.Codigo
    else:
        orderby = db.Alimento[request.vars.sidx]
    if request.vars.sord == 'desc':
        orderby = ~orderby
    query = (db.CabeceraAlmacen.alimento == db.Alimento.id) \
        & (db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera) \
        & (db.Alimento.Descripcion != None)

    if session.AlmacenAlimento:
        query = query & (db.Alimento.id == session.AlmacenAlimento)
    for r in db(query).select(
        db.CabeceraAlmacen.id,
        db.Alimento.Codigo,
        db.Alimento.Descripcion,
        db.Alimento.Conservacion,
        db.Alimento.Unidades,
        db.LineaAlmacen.Stock.sum(),
        limitby=limitby,
        orderby=orderby,
        groupby=db.CabeceraAlmacen.alimento,
    ):

        print db._lastsql

        vals = []
        for f in fields:
            if f == 'Stock':
                vals.append(r['_extra']['SUM(LineaAlmacen.Stock)'])
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
    fields = ['nada', 'Donante', 'Fecha', 'tipoProcedencia', 'Total']
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
    orderby = ~db.CabeceraEntrada.id
    query = db.CabeceraEntrada.id > 0
    if session.FechaAlmacen:
        query = query & (db.CabeceraEntrada.Fecha
                         == session.FechaAlmacen)
    if session.DonanteAlmacen:
        query = query & (db.CabeceraEntrada.Donante
                         == session.DonanteAlmacen)
    if session.ProcedenciaAlmacen:
        query = query & (db.CabeceraEntrada.tipoProcedencia
                         == session.ProcedenciaAlmacen)
    if session.AlmacenAlimento:
        query = query & (db.CabeceraEntrada.id
                         == db.LineaEntrada.cabecera)
        query = query & (db.LineaEntrada.alimento
                         == session.AlmacenAlimento)

    rowsentradas = db(query).select(db.CabeceraEntrada.ALL,
                                    limitby=limitby, orderby=orderby)

    # print db._lastsql

    for r in rowsentradas:

        # print db._lastsql

        vals = []
        for f in fields:
            if f == 'nada':
                vals.append('')
            elif f == 'Donante':
                vals.append(db.CabeceraEntrada['Donante'
                                               ].represent(r(f)))
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
    fields = ['nada', 'Beneficiario', 'Fecha', 'Total']
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

    # query = ""
    orderby = ~db.CabeceraSalida.id
    query = db.CabeceraSalida.id > 0
    if session.FechaAlmacen:
        query = query & (db.CabeceraSalida.Fecha
                         == session.FechaAlmacen)
    if session.BeneficiarioAlmacen:
        query = query & (db.CabeceraSalida.Beneficiario
                         == session.BeneficiarioAlmacen)
    if session.AlmacenAlimento:
        query = query & (db.CabeceraSalida.id
                         == db.LineaSalida.cabecera)
        query = query & (db.LineaSalida.alimento
                         == session.AlmacenAlimento)
    rowssalidas = db(query).select(db.CabeceraSalida.ALL,
                                   limitby=limitby, orderby=orderby)

    for r in rowssalidas:

        # print db._lastsql

        vals = []
        for f in fields:
            if f == 'nada':
                vals.append('')
            elif f == 'Beneficiario':
                vals.append(db.CabeceraSalida['Beneficiario'
                                              ].represent(r(f)))
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

    fields = ['Stock', 'Caducidad', 'PesoUnidad', 'stockinicial', 'Lote'
              ]
    rows = []
    cabecera_id = request.vars.id
    query = db.LineaAlmacen.cabecera == cabecera_id
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
    en_detalle = False
    limitby = None
    if 'id' in request.vars:
        cabecera_id = request.vars.id
    elif 'current_entrada' in session.keys():
        if session.current_entrada:
            cabecera_id = session.current_entrada
            page = int(request.vars.page)  # the page number
            pagesize = int(request.vars.rows)
            limitby = (page * pagesize - pagesize, page * pagesize)
            en_detalle = True
            fields = ['nada'] + fields

    if session.Entradas:
        query = db.LineaEntrada.cabecera == cabecera_id
        suma = db.LineaEntrada.Unidades.sum()
        ordenacion = ~db.LineaEntrada.id
    else:
        query = db.LineaSalida.cabecera == cabecera_id
        suma = db.LineaSalida.Unidades.sum()
        ordenacion = ~db.LineaSalida.id

    totales = db(query).select(suma)
    qty_totales = totales.first()[suma]
    locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')
    for r in db(query).select(limitby=limitby, orderby=ordenacion):
        vals = []
        for f in fields:
            if f == 'nada':
                vals.append('')
            elif f == 'Caducidad':
                k = r(f).strftime('%d/%m/%Y')
                vals.append(k)
            elif f == 'alimento':
                k = db.LineaEntrada['alimento'].represent(r(f))
                vals.append(k)
            elif f == 'Lote':
                vals.append(r[f] or '')
            else:
                vals.append(locale.format('%.2f', r[f], grouping=True))
        rows.append(dict(id=r.id, cell=vals))

    if en_detalle:
        if qty_totales:
            totales = locale.format('%.2f', qty_totales, grouping=True)
        else:
            totales = ''
        total = db(query).count()
        pages = math.ceil(1.0 * total / pagesize)
        data = dict(records=total, total=pages, page=page, rows=rows,
                    userdata={'qty_totales': totales})
        return data
    else:
        return response.json(dict(rows=rows))


@auth.requires_login()
@service.json
def get_lineas_almacen():
    fields = [
        'alimento',
        'Stock',
        'PesoUnidad',
        'Caducidad',
        'Lote',
        'estanteria',
        'Palets',
    ]
    rows = []
    limitby = None
    total = 0
    pages = 0
    page = int(request.vars.page)  # the page number
    pagesize = int(request.vars.rows)
    limitby = (page * pagesize - pagesize, page * pagesize)
    cabecera = db(db.CabeceraAlmacen.alimento
                  == session.AlmacenAlimento).select().first()
    if cabecera:
        query = (db.LineaAlmacen.cabecera == cabecera.id) \
            & (db.LineaAlmacen.Stock > 0)
        mialimento = db.CabeceraAlmacen['alimento'
                                        ].represent(cabecera.alimento)
        for r in db(query).select(limitby=limitby):
            vals = []
            for f in fields:
                if f == 'Caducidad':
                    if r(f):
                        k = r(f).strftime('%d/%m/%Y')
                    else:
                        k = ''
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


@auth.requires_login()
@service.json
def borra_entrada():
    if 'entrada_id' in request.vars:
        query = (db.LineaEntrada.cabecera == db.CabeceraEntrada.id) \
            & (db.CabeceraEntrada.id == request.vars.entrada_id)
        rows = db(query).select(db.LineaEntrada.id)
        for row in rows:
            borrar_linea(row.id)

        db(db.CabeceraEntrada.id == request.vars.entrada_id).delete()


@auth.requires_login()
@service.json
def borra_salida():
    if 'salida_id' in request.vars:
        query = (db.LineaSalida.cabecera == db.CabeceraSalida.id) \
            & (db.CabeceraSalida.id == request.vars.salida_id)
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
                session.FechaAlmacen = \
                    datetime.date(datetime.strptime(valor, '%d-%m-%Y'))
            else:
                session.FechaAlmacen = None
        elif parametro == 'donante':
            session.DonanteAlmacen = valor
        elif parametro == 'beneficiario':
            session.BeneficiarioAlmacen = valor
        elif parametro == 'procedencia':
            session.ProcedenciaAlmacen = valor
    return {}


@cache.action()
def download():
    return response.download(request, db)


def call():
    return service()


@auth.requires_signature()
def data():
    return dict(form=crud())


@auth.requires_login()
def repaso_almacen():
    # query = (db.LineaSalida.cabecera > 507) & (db.LineaEntrada.cabecera > 292)

    sumsalidas = db.LineaSalida.Unidades.sum()
    sumentradas = db.LineaEntrada.Unidades.sum()
    totales = []

    estado_11_11_2014 = {2: 1267.67, 3: 61.0, 4: 9.5, 6: 55.7, 7: 147.015,
                        9: 1423.8, 10: 8192.0, 11: 29114.5, 12: 7379.0, 14: 139.84,
                        17: 465.0, 19: 6443.25, 21: 21506.65, 22: 48.3, 23: 486.3,
                        24: 62.4, 25: 35.3, 28: 10393.2, 43: 0.0, 45: 6643.55,
                        46: 235.0, 51: 163.04, 99: 276.0}

    filas = db(db.LineaSalida.cabecera > 507).select(
        db.LineaSalida.alimento, sumsalidas, groupby=db.LineaSalida.alimento)
    filase = db(db.LineaEntrada.cabecera > 292).select(
        db.LineaEntrada.alimento, sumentradas, groupby=db.LineaEntrada.alimento)

    totales = {}

    for fila in filase:
        totales[fila.LineaEntrada.alimento] = fila[sumentradas]

    for fila in filas:
        if fila.LineaSalida.alimento in totales.keys():
            totales[fila.LineaSalida.alimento] = totales[
                fila.LineaSalida.alimento] - fila[sumsalidas]
        else:
            totales[fila.LineaSalida.alimento] = - fila[sumsalidas]
    for estado in estado_11_11_2014:
        try:
            totales[estado] = estado_11_11_2014[estado] + totales[estado]
            totales[estado] = float("{0:.3f}".format(totales[estado]))
        except:
            pass

    return dict(totales=totales)


@auth.requires_login()
def importarsalida():
    
    hoja_form = FORM(
        INPUT(_name='sheet_title', _type='text'),
        INPUT(_name='sheet_file', _type='file')
        )

    if hoja_form.accepts(request.vars, formname='hoja_form'):
        import xlrd
        print hoja_form.vars.sheet_file.filename
        archivo = hoja_form.vars.sheet_file.file
        try:
            wb = xlrd.open_workbook(file_contents=archivo.read())
            sheets = wb.sheets()
            for hoja in sheets:
                importa_hoja_salida(hoja)
        except:
            pass
    
    return dict()

def importa_hoja_salida(hoja):
    row = hoja.row(1)  # 2 fila
    print row


    
