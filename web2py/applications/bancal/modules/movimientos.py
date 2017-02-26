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
from datetime import datetime, date
from gluon import current

__all__ = ['check_stock', 'actualiza_lineaalmacen', 'nueva_lineaalmacen',
           'borrar_linea', 'get_alimentos', 'get_donante', 'set_donante',
           'search_form', 'search_query', 'stock_alimento', 'ultima_salida',
           'insertar_salida', 'actualizar_almacen_linea_salida',
           'insertar_linea_salida']


def check_stock(form):
    """Comprueba que hay stock disponible, dependiendo de:
    - valor que se ha pedido ahora:stock_pendiente
    - stock en el almacén: stock_actual
    - Si se está editando una línea que ya tenía stock anteriormente descontado
    hay que tenerlo en cuenta: session.valor_antiguo. Si la línea es nueva esto valdrá 0
    """
    db = current.db
    stock_pendiente = float(form.vars.Unidades)
    query = (db.CabeceraAlmacen.alimento == form.vars.alimento) \
        & (db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)
    stock_actual = \
        db(query).select(db.LineaAlmacen.Stock.sum()).first()[
            db.LineaAlmacen.Stock.sum()]
    # if stock_pendiente - session.valor_antiguo > stock_actual:
    #     stock_pendiente = stock_actual + session.valor_antiguo
    #     form.vars.Unidades = stock_pendiente
    #     form.vars.LineaAlmacen = \
    #         db(query).select(db.LineaAlmacen.id).first().id


def stock_alimento(codigo, db1):
    """Devuelve, dado el código de un alimento:
    Un diccionario conteniendo
    - alimento: nombre del alimento
    - id: id del alimento en la tabla db1.Alimento
    - stock: stock disponible del alimento
    - stock-text: stock disponible del alimento formateado como texto
    """
    data = {'alimento': '', 'id': None, 'stock': None, 'stock-text': None}
    alimento = db1((db1.Alimento.Codigo == codigo) & (db1.Alimento.Descripcion != None)).select().first()
    if alimento:
        data['alimento'] = alimento.Descripcion
        data['id'] = alimento.id

        query = (db1.CabeceraAlmacen.alimento == db1.Alimento.id) \
            & (db1.CabeceraAlmacen.id == db1.LineaAlmacen.cabecera)
        query = query & (db1.Alimento.id == alimento.id)
        stock = db1(query).select(db1.LineaAlmacen.Stock.sum()).first()[db1.LineaAlmacen.Stock.sum()]
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


def nueva_lineaalmacen(valores, es_entrada=False):
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
    query = query & (db.LineaAlmacen.Caducidad <= fecha_caducidad)
    query = query & (db.LineaAlmacen.estanteria == valores.estanteria)
    query = query & (db.LineaAlmacen.Lote == valores.Lote)
    linea = db(query).select(db.LineaAlmacen.id, orderby=db.LineaAlmacen.Stock).first()
    if linea:
        if es_entrada:
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


def borrar_linea(linea_id=None, es_entrada = False):
    db = current.db
    if linea_id:
        if es_entrada:
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


def insertar_salida(beneficiario_id, fecha, almacen=1):
    db = current.db
    record = db.CabeceraSalida.insert(Beneficiario=beneficiario_id, Fecha=fecha, almacen=almacen)
    return record


def ultima_salida():
    db = current.db
    record = db(db.CabeceraSalida.id > 0).select(db.CabeceraSalida.id, orderby=db.CabeceraSalida.id)
    if len(record) > 0:
        return record.first().id
    else:
        return 0


def actualizar_almacen_linea_salida(alimento_id, uds, valor_antiguo_uds=0):
    # param: valor_antiguo_uds usado si estoy editando, no añadiendo una línea
    db = current.db
    stock_pendiente = uds
    query = (db.CabeceraAlmacen.alimento == alimento_id) \
                & (db.CabeceraAlmacen.id == db.LineaAlmacen.cabecera)
    lineas_almacen = db(query).select(db.LineaAlmacen.id, db.LineaAlmacen.Stock, orderby=~db.LineaAlmacen.Stock)
    if valor_antiguo_uds > 0:
        actualiza_lineaalmacen(lineas_almacen.first().id,  valor_antiguo_uds, stock_pendiente)
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


def insertar_linea_salida(cabecera_id, alimento_id, uds, caducidad=None, lote='', peso_unidad=1.0, valor_antiguo_uds=0):
    # no usando: precio_kg, estanteria, LineaAlmacen
    db = current.db
    if caducidad is None:
        caducidad = date(9999, 12, 31)
    elif isinstance(caducidad, str):
        caducidad = datetime.strptime(caducidad, '%d-%m-%Y').date()
    
    record = db.LineaSalida.insert(cabecera=cabecera_id, alimento=alimento_id, Unidades=uds, PesoUnidad=peso_unidad, Caducidad=caducidad, Lote=lote)
    actualizar_almacen_linea_salida(alimento_id, uds)
    return record
