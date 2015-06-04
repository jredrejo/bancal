# -*- coding: utf-8 -*-
if 0:  # for IDE's to find the imports for the globals
    from gluon.globals import *
    from gluon.html import *
    from gluon.http import redirect
    from gluon.tools import *
    from gluon.sql import *
    from gluon.validators import *
    from gluon.languages import translator as T
    from gluon.sqlhtml import SQLFORM, SQLTABLE, form_factory
    from gluon import compileapp
    from gluon import tools, sql, compileapp
    from gluon.languages import translator as T
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
    db = DAL('sqlite://storage.sqlite')
    auth = Auth(globals(), None)


class Almacen(object):

    def __init__(id, db, cierre='2001-01-01'):
        self.id = id
        self.db = db
        self.cierre = cierre


def nueva_entrada(self, current_entrada, id_alimento, unidades):

    registro = None
    if current_entrada:
        registro = self.db.CabeceraEntrada(current_entrada)
        NuevaLinea = True


    if current_entrada:
        valor_antiguo_uds = None
        if id_alimento:
            registro_linea = self.db.LineaEntrada(id_alimento)
            registro_alimento = self.db.Alimento(registro_linea.alimento)
            codigo_alimento = registro_alimento.Codigo
            session.NuevaLinea = True
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
            session.NuevaLinea = True
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
