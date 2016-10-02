# -*- coding: utf-8 -*-
if 0:  # for IDE's to find the imports for the globals
    from gluon.globals import *
    from gluon.html import *
    from gluon.http import redirect
    from gluon.tools import *
    from gluon.sql import *
    from gluon.validators import *
    from gluon.dal import DAL
    from gluon.sqlhtml import *
    from gluon.html import URL
    from gluon.validators import *
    global LOAD
    LOAD = compileapp.LoadFactory()
    global request
    request = globals.Request()
    global response
    response = globals.Response()
    global session
    session = globals.Session()
    global cache
    cache = cache.Cache
    auth = Auth(globals(), None)

import locale
from datetime import datetime
from gluon import current
session = current.session

__all__ = ['ver_cierre', 'check_stock', 'actualiza_lineaalmacen', 'nueva_lineaalmacen',
           'borrar_linea', 'get_alimentos', 'get_donante', 'set_donante',
           'search_form', 'search_query', 'stock_alimento']


def ver_cierre(form):
    if session.cierre:
        if form.vars.Fecha < session.cierre:
            form.errors.Fecha = 'El almacén está cerrado para esa fecha'


def check_stock(form):
    """Comprueba que hay stock disponible, dependiendo de:
    - valor que se ha pedido ahora:stock_pendiente
    - stock en el almacén: stock_actual
    - Si se está editando una línea que ya tenía stock anteriormente descontado
    hay que tenerlo en cuenta: session.valor_antiguo. Si la línea es nueva esto valdrá 0
    """
    # db = form.table._db
    db = current.db
    stock_pendiente = float(form.vars.Unidades)
    query = (db.CabeceraAlmacen.alimento == form.vars.alimento) \
        & (db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)
    stock_actual = \
        db(query).select(db.LineaAlmacen.Stock.sum()).first()[
            db.LineaAlmacen.Stock.sum()]
    if stock_pendiente - session.valor_antiguo > stock_actual:
        stock_pendiente = stock_actual + session.valor_antiguo
        form.vars.Unidades = stock_pendiente
        form.vars.LineaAlmacen = \
            db(query).select(db.LineaAlmacen.id).first().id


def stock_alimento(codigo, db1):
    """Devuelve, dado el código de un alimento:
    Un diccionario conteniendo
    - alimento: nombre del alimento
    - id: id del alimento en la tabla db.Alimento
    - stock: stock disponible del alimento
    - stock-text: stock disponible del alimento formateado como texto
    """
    db = current.db
    data = {'alimento': '', 'id': None, 'stock': None, 'stock-text': None}
    alimento = db((db.Alimento.Codigo == codigo) & (db.Alimento.Descripcion != None)).select().first()
    if alimento:
        data['alimento'] = alimento.Descripcion
        data['id'] = alimento.id

        query = (db.CabeceraAlmacen.alimento == db.Alimento.id) \
            & (db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)
        query = query & (db.Alimento.id == alimento.id)
        stock = db(query).select(db.LineaAlmacen.Stock.sum()).first()[db.LineaAlmacen.Stock.sum()]
        if not stock:
            stock = 0
        locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')
        data['stock'] = stock
        data['stock-text'] = locale.format('%.2f', stock, grouping=True)

    return data


def actualiza_lineaalmacen(linea, valornuevo, valorprevio=None):
    """Descuenta o añade stock en una línea de almacén, según el orden de valornuevo y valorprevio"""
    db = current.db
    registro = db.LineaAlmacen(linea)
    total = float(registro.Stock)
    # Limito a tres decimales en el stock
    registro.Stock = float("{0:.3f}".format(total + valornuevo - valorprevio))

    # if registro.Stock<0: registro.Stock =0
    registro.update_record()


def nueva_lineaalmacen(valores):
    db = current.db
    cabecera = db(db.CabeceraAlmacen.alimento == valores.alimento).select().first()
    if not cabecera:
        cid = db.CabeceraAlmacen.insert(alimento=valores.alimento)
    else:
        cid = cabecera.id
    if not valores.Caducidad:
        fecha_caducidad = datetime.datetime(2999, 12, 31)
    else:
        fecha_caducidad = datetime.strptime(valores.Caducidad, '%d-%m-%Y')
    query = (db.LineaAlmacen.cabecera == cid) \
        & (db.LineaAlmacen.PesoUnidad == valores.PesoUnidad)
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
            cabecera=cid,
            PesoUnidad=valores.PesoUnidad,
            Caducidad=fecha_caducidad,
            estanteria=valores.estanteria,
            Lote=valores.Lote,
            Stock=float(valores.Unidades),
        )
    return lid


def borrar_linea(linea_id=None):
    db = current.db
    if linea_id:
        if session.Entradas:
            registro = db.LineaEntrada(linea_id)
            if registro.LineaAlmacen > 0:
                actualiza_lineaalmacen(registro.LineaAlmacen, 0,
                                       registro.Unidades)
            db(db.LineaEntrada.id == linea_id).delete()
        else:
            registro = db.LineaSalida(linea_id)
            cabecera = db(db.CabeceraAlmacen.alimento
                          == registro.alimento).select().first()
            query = db.LineaAlmacen.cabecera == cabecera.id
            linea_almacen = db(query).select(db.LineaAlmacen.id,
                                             orderby=~db.LineaAlmacen.Stock).first()

            # metemos el stock de la línea borrada en la lína
            # de stock que más tenga. No se lleva registro de las
            # líneas de almacén que hubiera antes:

            if linea_almacen:
                actualiza_lineaalmacen(linea_almacen.id,
                                       registro.Unidades, 0)
            db(db.LineaSalida.id == linea_id).delete()


def get_alimentos():
    db = current.db
    q = request.vars.term
    if q:
        search_term = q.lower().replace(' ', '-')
        query = db.Alimento.Descripcion.contains(search_term)

        rows = db(query).select(db.Alimento.Descripcion)
        return response.json([s['Descripcion'] for s in rows])

    return ''


def get_donante():
    db = current.db
    q = request.vars.term
    if q:
        query = db.Colaborador.name.contains(q) \
            & (db.Colaborador.Donante == True)
        rows = db(query).select(db.Colaborador.name)
        return response.json([s['name'] for s in rows])

    return ''


def set_donante():
    db = current.db
    q = request.vars.donante
    if q:
        query = (db.Colaborador.name == q) & (db.Colaborador.Donante
                                              == True)
        row = db(query).select(db.Colaborador.name,
                               db.Colaborador.id).first()
        data = {'donante': row.id}
        data = row.id
        return data
    return ''


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


class Almacen(object):

    def __init__(self, id, db, cierre='2001-01-01'):
        self.id = id
        self.db = db
        self.cierre = cierre

    def actualiza_lineaalmacen(self, linea, valornuevo, valorprevio=None):
        """Descuenta o añade stock en una línea de almacén,
        según el orden de valornuevo y valorprevio"""

        registro = self.db.LineaAlmacen(linea)
        total = float(registro.Stock)
        # Limito a tres decimales en el stock
        registro.Stock = float("{0:.3f}".format(total + valornuevo - valorprevio))

        # if registro.Stock<0: registro.Stock =0
        registro.update_record()

    def nueva_entrada(self, current_entrada, id_alimento, unidades):

        valor_antiguo_uds = None

        if current_entrada:
            valor_antiguo_uds = None
            if id_alimento:
                registro_linea = self.db.LineaEntrada(id_alimento)
                registro_alimento = self.db.Alimento(registro_linea.alimento)
                codigo_alimento = registro_alimento.Codigo
                if unidades:
                    if float(unidades) \
                            != registro_linea.Unidades:
                        valor_antiguo_uds = registro_linea.Unidades
            else:
                registro_linea = None
                codigo_alimento = XML('""')

            self.db.LineaEntrada.cabecera.default = current_entrada

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

        return dict(form=form, frmlineas=frmlineas,
                    codigo_alimento=codigo_alimento)
