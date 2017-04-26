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


# No olvidar instalar en el servidor: apt-get install python-dateutil

from datetime import date
from dateutil import relativedelta
import locale
import xlwt
import cStringIO
from xlwt import CompoundDoc
locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')


@auth.requires_login()
def mes():
    nombre_mes = None
    nombre_year = None
    tabla_informe = None
    years = range(2013, date.today().year + 1)
    months = (
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio',
        'Julio',
        'Agosto',
        'Septiembre',
        'Octubre',
        'Noviembre',
        'Diciembre',
        )

    form = SQLFORM.factory(Field('year', label="Año",
                           requires=IS_IN_SET(years)), Field('mes',
                           requires=IS_IN_SET(months)),
                           submit_button='Generar informe mensual')
    fecha_pasada = date.today() - relativedelta.relativedelta(months=1)
    form.vars.year = fecha_pasada.year
    form.vars.mes = months[fecha_pasada.month - 1]

    if form.accepts(request, session):
        session.nombre_mes = form.vars.mes
        session.nombre_year = form.vars.year
        session.informe = \
            generar_informe(months.index(session.nombre_mes) + 1,
                            int(session.nombre_year))
        tabla_informe = generar_tabla(session.informe)
    else:
        session.informe = None

    return dict(form=form, tabla_informe=tabla_informe)


@auth.requires_login()
def trimestre():
    nombre_trimestre = None
    nombre_year = None
    tabla_informe = None
    years = range(2013, date.today().year + 1)
    trimestres = ('PRIMERO', 'SEGUNDO', 'TERCERO', 'CUARTO')

    form = SQLFORM.factory(Field('year', label="Año",
                           requires=IS_IN_SET(years)), Field('trimestre'
                           , requires=IS_IN_SET(trimestres)),
                           submit_button='Generar informe trimestral')
    fecha_pasada = date.today() - relativedelta.relativedelta(months=3)
    form.vars.year = fecha_pasada.year
    form.vars.trimestre = trimestres[(fecha_pasada.month - 1) // 3]

    if form.accepts(request, session):
        session.nombre_trimestre = form.vars.trimestre
        session.nombre_year = form.vars.year
        session.informe = \
            generar_informe(trimestres.index(session.nombre_trimestre),
                            int(session.nombre_year), trimestre=True)
        tabla_informe = generar_tabla(session.informe)
    else:
        session.informe = None

    return dict(form=form, tabla_informe=tabla_informe)


def cabecera_informe(sheet, trimestre=False):
    ezxf = xlwt.easyxf
    style_hidden = \
        ezxf('font: name CG Times (WN), bold True, height 220;alignment: vertical top,horizontal center;border: top medium, left medium,right medium,bottom thin'
             )

    style_hidden2 = \
        ezxf('font: name CG Times (WN), bold True, height 220;alignment: vertical center,horizontal center;border: top thin, left medium,right medium,bottom thin'
             )

    sheet.write_merge(
        0,
        2,
        0,
        10,
        'FEDERACIÓN   ESPAÑOLA   DE   BANCOS    DE    ALIMENTOS\nBANCO    DE    ALIMENTOS    DE  BADAJOZ'
            ,
        style_hidden,
        )
    if trimestre:
        sheet.write_merge(
            3,
            3,
            0,
            10,
            'ENTRADAS Y SALIDAS DE ALIMENTOS EN EL '
                + session.nombre_trimestre + ' TRIMESTRE DE '
                + session.nombre_year,
            style_hidden2,
            )
    else:
        sheet.write_merge(
            3,
            3,
            0,
            10,
            'ENTRADAS Y SALIDAS DE ALIMENTOS EN ' + session.nombre_mes
                + ' DE ' + session.nombre_year,
            style_hidden2,
            )
    style2 = \
        ezxf('font: name CG Times (WN), bold False, height 200;alignment: horizontal center;border: top thin, left thin,right thin,bottom thin'
             )

    sheet.write_merge(
        4,
        4,
        0,
        4,
        'Número de Asociaciones Benéficas atendidas: ',
        style2,
        )
    sheet.write_merge(
        4,
        4,
        6,
        8,
        'Número de beneficiarios:',
        style2,
        )
    style3 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top medium, left medium,right medium,bottom medium'
             )

    sheet.write_merge(
        5,
        7,
        0,
        0,
        '',
        style3,
        )
    sheet.write_merge(
        5,
        5,
        1,
        7,
        'C A N T I D A D E S     R E C I B I D A S  (KG)',
        style3,
        )
    sheet.write_merge(
        5,
        5,
        8,
        10,
        'CANTID. SUMINISTRADAS (KG)',
        style3,
        )
    style4 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top medium, left thin,right thin,bottom medium'
             )

    sheet.write_merge(
        6,
        7,
        1,
        1,
        'ESTADO',
        style4,
        )
    sheet.write_merge(
        6,
        7,
        2,
        2,
        'UNIÓN\nEUROPEA',
        style4,
        )
    sheet.write_merge(
        6,
        7,
        3,
        3,
        'INDUSTRIA',
        style4,
        )
    sheet.write_merge(
        6,
        7,
        4,
        4,
        'DISTRIB.',
        style4,
        )
    sheet.write_merge(
        6,
        7,
        5,
        5,
        'COLECTAS',
        style4,
        )
    style5 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top medium, left thin,right medium,bottom no_line'
             )

    sheet.write_merge(
        6,
        6,
        6,
        7,
        'OTROS BANCOS (1)',
        style5,
        )
    style6 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top no_line, left thin,right no_line,bottom medium'
             )

    sheet.write(7, 6, 'Nombre', style6)
    style7 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top no_line, left no_line,right medium,bottom medium'
             )

    sheet.write(7, 7, 'Cantidad', style7)
    style8 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top medium, left thin,right thin,bottom no_line'
             )

    sheet.write_merge(
        6,
        6,
        8,
        9,
        'OTROS BANCOS (1)',
        style8,
        )
    sheet.write(7, 8, 'Nombre', style6)
    style9 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top no_line, left no_line,right thin,bottom medium'
             )

    sheet.write(7, 9, 'Cantidad', style9)
    sheet.write_merge(
        6,
        7,
        10,
        10,
        'ASOCIA-\nCIONES',
        style7,
        )
    style10 = \
        ezxf('font: name CG Times (WN), bold False, height 200;alignment: horizontal center;border: top thin, left medium,right medium,bottom medium'
             )

    sheet.write(4, 5, session.informe['TOT']['bens'], style10)
    sheet.write(4, 10, session.informe['TOT']['beneficiarios'], style10)
    sheet.col(0).width = 1340  # 1,02 cm,0,000761194 cm/pt
    sheet.row(3).height = 310  # 0.55cm
    return sheet


@auth.requires_login()
def descargar_tabla_trimestre():
    return crear_xls(trimestre=True)


@auth.requires_login()
def descargar_tabla():
    return crear_xls()


def crear_xls(trimestre=False):
    ezxf = xlwt.easyxf
    book = xlwt.Workbook(encoding='utf-8')
    if trimestre:
        sheet = book.add_sheet(session.nombre_trimestre)
    else:
        sheet = book.add_sheet(session.nombre_mes)
    data_xfs = [
        ezxf(num_format_str='#,##0'),
        ezxf(),
        ezxf(),
        ezxf(num_format_str='#,##0'),
        ezxf(num_format_str='#,##0'),
        ezxf(num_format_str='#,##0'),
        ezxf(num_format_str='#,##0'),
        ]
    cabecera_informe(sheet, trimestre)
    codigos = session.informe.keys()
    fila = 8
    style11 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top dotted, left thin,right medium,bottom dotted'
             )

    style12 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top dotted, left thin,right thin,bottom dotted'
             )

    style13 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal right,vertical center;border: top dotted, left thin,right medium,bottom dotted'
             )

    style14 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal right,vertical center;border: top dotted, left thin,right thin,bottom dotted'
             )

    for codigo in codigos:
        elemento = session.informe[codigo]
        if codigo != 'TOT':
            sheet.write(fila, 0, codigo, style11)
            sheet.write(fila, 1, quita_none_float(elemento['ESTADO']),
                        style14)
            sheet.write(fila, 2, elemento["UNIÓN EUROPEA"], style14)
            sheet.write(fila, 3, quita_none_float(elemento['INDUSTRIA'
                        ]), style14)
            sheet.write(fila, 4, elemento["DISTRIBUCIÓN"], style14)
            sheet.write(fila, 5, elemento['COLECTAS'], style14)
            sheet.write(fila, 6, elemento['eNombre'], style12)
            sheet.write(fila, 7, elemento['eCantidad'], style14)
            sheet.write(fila, 8, elemento['sNombre'], style12)
            sheet.write(fila, 9, elemento['OTROS BANCOS'], style14)
            sheet.write(fila, 10, elemento['ASOCIACIONES'], style13)
            fila += 1

    # pie de hoja:

    style15 = \
        ezxf('font: name CG Times (WN), bold True, height 160;alignment: horizontal center,vertical center;border: top medium, left thin,right thin,bottom medium'
             )

    sheet.write(fila, 0, 'TOT', style15)
    style15 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal right,vertical center;border: top medium, left thin,right thin,bottom medium'
             )

    sheet.write(fila, 1, xlwt.Formula('SUM(B9:B' + str(fila) + ')'),
                style15)
    sheet.write(fila, 2, xlwt.Formula('SUM(C9:C' + str(fila) + ')'),
                style15)
    sheet.write(fila, 3, xlwt.Formula('SUM(D9:D' + str(fila) + ')'),
                style15)
    sheet.write(fila, 4, xlwt.Formula('SUM(E9:E' + str(fila) + ')'),
                style15)
    sheet.write(fila, 5, xlwt.Formula('SUM(F9:F' + str(fila) + ')'),
                style15)
    sheet.write(fila, 6, '', style15)
    sheet.write(fila, 7, xlwt.Formula('SUM(H9:H' + str(fila) + ')'),
                style15)
    sheet.write(fila, 8, '', style15)
    sheet.write(fila, 9, xlwt.Formula('SUM(J9:J' + str(fila) + ')'),
                style15)
    style16 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal right,vertical center;border: top medium, left thin,right medium,bottom medium'
             )

    sheet.write(fila, 10, xlwt.Formula('SUM(K9:K' + str(fila) + ')'),
                style16)
    style8 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top medium, left thin,right thin,bottom no_line'
             )

    sheet.write_merge(
        fila + 1,
        fila + 1,
        0,
        2,
        'STOCK  a comienzo de mes:',
        style8,
        )
    sheet.write_merge(
        fila + 1,
        fila + 1,
        3,
        4,
        '+ TOTAL  RECIBIDO:',
        style8,
        )
    sheet.write_merge(
        fila + 1,
        fila + 1,
        5,
        6,
        '- TOTAL ENTREGADO:',
        style8,
        )
    sheet.write_merge(
        fila + 1,
        fila + 1,
        7,
        8,
        '  -  DESVIACIONES (2)',
        style8,
        )
    style5 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top medium, left thin,right medium,bottom no_line'
             )

    sheet.write_merge(
        fila + 1,
        fila + 1,
        9,
        10,
        '  =  STOCK a fin de mes',
        style5,
        )
    style6 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal center,vertical center;border: top no_line, left no_line,right no_line,bottom medium'
             )

    for col in (
        0,
        1,
        3,
        5,
        7,
        9,
        ):
        sheet.write(fila + 2, col, '', style6)
    style10 = \
        ezxf('font: name CG Times (WN), bold False, height 200;alignment: horizontal center, vertical center;border: top medium, left medium,right medium,bottom medium'
             )

    sheet.write(fila + 2, 2, session.total_previo, style10)
    sheet.write(fila + 2, 8, '', style10)
    sheet.write(fila + 2, 4, xlwt.Formula('SUM(B' + str(fila + 1) + ':H'
                 + str(fila + 1) + ')'), style10)
    sheet.write(fila + 2, 6, xlwt.Formula('SUM(I' + str(fila + 1) + ':K'
                 + str(fila + 1) + ')'), style10)
    sheet.write(fila + 2, 10, xlwt.Formula('C' + str(fila + 3) + '+E'
                + str(fila + 3) + '-G' + str(fila + 3) + '-I'
                + str(fila + 3)), style10)
    texto_pie = \
        "Notas:\t(1)  Indicar, por su código, los Bancos que han donado o recibido productos.\n"
    texto_pie += \
        '''\t(2)  Justificar las desviaciones sobre el STOCK.\t\t\t\t\t\t


'''
    texto_pie += \
        'Nombre del respons.:\t\t\t\t\t\t\tFirma:\t\t\t\t\t\tTlfno:\t\t\t\t\tFecha:\t\t\t\t '
    sheet.write_merge(
        fila + 3,
        fila + 7,
        0,
        10,
        texto_pie,
        style10,
        )

    s = cStringIO.StringIO()
    doc = CompoundDoc.XlsDoc()
    doc.save(s, book.get_biff_data())

    response.headers['Content-Type'] = 'application/vnd.ms-excel'
    if trimestre:
        response.headers['Content-Disposition'] = \
            'attachment; filename=Informe' + session.nombre_trimestre \
            + session.nombre_year + '.xls'
    else:
        response.headers['Content-Disposition'] = \
            'attachment; filename=Informe' + session.nombre_mes \
            + session.nombre_year + '.xls'
    return s.getvalue()


def quita_none(valor):
    if valor:
        return locale.format('%.2f', float(valor), grouping=True)
    else:
        return ' '


def quita_none_string(valor):
    if valor:
        return valor
    else:
        return ' '


def quita_none_float(valor):
    if valor:
        return float(valor)
    else:
        return None


def generar_tabla(informe):
    cabecera1 = (TH('CANTIDADES RECIBIDAS (KG)', _width='80%',
                 _colspan='8', _class='informe'),
                 TH('CANTID. SUMINISTRADAS (KG)', _width='20%',
                 _colspan='3', _class='informe'))
    cabecera2 = (
        TH(' ', _class='informe2'),
        TH('ESTADO', _class='informe2'),
        TH('UE', _class='informe2'),
        TH('INDUSTRIA', _class='informe2'),
        TH('DISTRIB.', _class='informe2'),
        TH('COLECTAS', _class='informe2'),
        TH('OTROS BANCOS', _colspan='2', _class='informe'),
        TH('OTROS BANCOS', _colspan='2', _class='informe'),
        TH('ASOCIACIONES', _class='informe2'),
        )
    cabecera3 = (
        TH(' ', _class='informe3'),
        TH(' ', _class='informe3'),
        TH(' ', _class='informe3'),
        TH(' ', _class='informe3'),
        TH(' ', _class='informe3'),
        TH(' ', _class='informe3'),
        TH('Nombre', _class='informe'),
        TH('Cantidad', _class='informe'),
        TH('Nombre', _class='informe'),
        TH('Cantidad', _class='informe'),
        TH(' ', _class='informe3'),
        )

    head = THEAD(TR(_bgcolor='#A0A0A0', *cabecera1),
                 TR(_bgcolor='#B0B0B0', *cabecera2),
                 TR(_bgcolor='#B0B0B0', *cabecera3))
    filas = []
    codigos = informe.keys()
    i = 1
    for codigo in codigos:
        col = i % 2 and '#E3E3E3' or '#FFFFFF'
        col_clas = i % 2 and 'even' or 'odd'
        i += 1
        elemento = informe[codigo]
        if codigo == 'TOT':
            pie = (
                TD(codigo, _class='pieinforme'),
                TD(quita_none(elemento['ESTADO']), _class='pieinforme'
                   ),
                TD(quita_none(elemento["UNIÓN EUROPEA"]),
                   _class='pieinforme'),
                TD(quita_none(elemento['INDUSTRIA']),
                   _class='pieinforme'),
                TD(quita_none(elemento["DISTRIBUCIÓN"]),
                   _class='pieinforme'),
                TD(quita_none(elemento['COLECTAS']), _class='pieinforme'
                   ),
                TD('', _class='pieinforme'),
                TD(quita_none(elemento['eCantidad']),
                   _class='pieinforme'),
                TD('', _class='pieinforme'),
                TD(quita_none(elemento['OTROS BANCOS']),
                   _class='pieinforme'),
                TD(quita_none(elemento['ASOCIACIONES']),
                   _class='pieinforme'),
                )
        else:
            datos_elemento = (
                TD(codigo),
                TD(quita_none(elemento['ESTADO'])),
                TD(quita_none(elemento["UNIÓN EUROPEA"])),
                TD(quita_none(elemento['INDUSTRIA'])),
                TD(quita_none(elemento["DISTRIBUCIÓN"])),
                TD(quita_none(elemento['COLECTAS'])),
                TD(quita_none_string(elemento['eNombre'])),
                TD(quita_none(elemento['eCantidad'])),
                TD(quita_none_string(elemento['sNombre'])),
                TD(quita_none(elemento['OTROS BANCOS'])),
                TD(quita_none(elemento['ASOCIACIONES'])),
                )
            filas.append(TR(_bgcolor=col, _class=col_clas,
                         *datos_elemento))

    body = TBODY(*filas)
    foot = TFOOT(TR(*pie))

    tabla = TABLE(_border='1', _align='center', _width='100%', *[head,
                  body, foot])
    return tabla


def generar_informe(mes, year, trimestre=False):
    if trimestre:
        fecha1 = date(year, mes * 3 + 1, 1)
        fecha2 = fecha1 + relativedelta.relativedelta(months=3)
    else:
        fecha1 = date(year, mes, 1)
        fecha2 = fecha1 + relativedelta.relativedelta(months=1)
    informe = {}
    fila_informe = {
        'ESTADO': None,
        "UNIÓN EUROPEA": None,
        'INDUSTRIA': None,
        "DISTRIBUCIÓN": None,
        'COLECTAS': None,
        'eNombre': None,
        'eCantidad': None,
        'sNombre': None,
        'OTROS BANCOS': None,
        'ASOCIACIONES': None,
        }
    codigos = db(db.Alimento.Descripcion
                 != None).select(db.Alimento.Codigo,
                                 orderby=db.Alimento.Codigo)
    for codigo in codigos:
        informe[codigo.Codigo] = {
            'ESTADO': None,
            "UNIÓN EUROPEA": None,
            'INDUSTRIA': None,
            "DISTRIBUCIÓN": None,
            'COLECTAS': None,
            'eNombre': None,
            'eCantidad': None,
            'sNombre': None,
            'OTROS BANCOS': None,
            'ASOCIACIONES': None,
            }
    informe['TOT'] = fila_informe

    campo = db.LineaEntrada.Unidades.sum()

    # totales previos

    query = (db.CabeceraEntrada.Fecha < fecha1) \
        & (db.LineaEntrada.cabecera == db.CabeceraEntrada.id)
    rows = db(query).select(campo)
    try:
        total_entradas = rows.first()[campo]
    except:
        total_entradas = 0
    if not total_entradas:
        total_entradas = 0
    query = (db.CabeceraSalida.Fecha < fecha1) \
        & (db.LineaSalida.cabecera == db.CabeceraSalida.id)
    campo2 = db.LineaSalida.Unidades.sum()
    rows = db(query).select(campo2)
    try:
        total_salidas = rows.first()[campo2]
    except:
        total_salidas = 0
    if not total_salidas:
        total_salidas = 0
    session.total_previo = total_entradas - total_salidas

    # ENTRADAS:

    query = (db.CabeceraEntrada.Fecha < fecha2) \
        & (db.CabeceraEntrada.Fecha >= fecha1)

    query1 = query & (db.LineaEntrada.cabecera == db.CabeceraEntrada.id)

    # totales:

    rows = db(query1).select(db.CabeceraEntrada.tipoProcedencia, campo,
                             groupby=db.CabeceraEntrada.tipoProcedencia)
    for row in rows:
        if row.CabeceraEntrada.tipoProcedencia != 'OTROS BANCOS':
            informe['TOT'][row.CabeceraEntrada.tipoProcedencia] = \
                row[campo]
        else:
            informe['TOT']['eCantidad'] = row[campo]

    # por código:

    rows = db(query1).select(db.LineaEntrada.alimento,
                             db.CabeceraEntrada.tipoProcedencia, campo,
                             groupby=(db.LineaEntrada.alimento,
                             db.CabeceraEntrada.tipoProcedencia))
    for row in rows:
        codigo_alimento = db.Alimento[row.LineaEntrada.alimento].Codigo
        if row.CabeceraEntrada.tipoProcedencia != 'OTROS BANCOS':
            try:
                informe[codigo_alimento][row.CabeceraEntrada.tipoProcedencia] = \
                    row[campo]
            except:
                print row.LineaEntrada.alimento
        else:
            query2 = query1 & (db.LineaEntrada.alimento
                               == row.LineaEntrada.alimento) \
                & (db.CabeceraEntrada.tipoProcedencia == 'OTROS BANCOS'
                   ) & (db.CabeceraEntrada.Donante == db.Colaborador.id)
            bancos = db(query2).select(db.Colaborador.name)
            if len(bancos) > 1:
                informe[codigo_alimento]['eNombre'] = 'Varios'
            else:
                if bancos.first().name[:5] == 'BANCO':

                    informe[codigo_alimento]['eNombre'] = \
                        bancos.first().name[6:]
                else:
                    informe[codigo_alimento]['eNombre'] = \
                        'Varios'
            informe[codigo_alimento]['eCantidad'] = row[campo]

    # SALIDAS:

    campo = db.LineaSalida.Unidades.sum()
    query = (db.CabeceraSalida.Fecha < fecha2) \
        & (db.CabeceraSalida.Fecha >= fecha1)
    query1 = query & (db.LineaSalida.cabecera == db.CabeceraSalida.id)
    query1 = query1 & (db.CabeceraSalida.Beneficiario
                       == db.Beneficiario.id)

    # totales:

    rows = db(query1).select(db.Beneficiario.tipobeneficiario, campo,
                             groupby=db.Beneficiario.tipobeneficiario)
    for row in rows:
        informe['TOT'][row.Beneficiario.tipobeneficiario] = row[campo]

    # por codigo:

    rows = db(query1).select(db.LineaSalida.alimento,
                             db.Beneficiario.tipobeneficiario, campo,
                             groupby=(db.LineaSalida.alimento,
                             db.Beneficiario.tipobeneficiario))
    for row in rows:
        codigo_alimento = db.Alimento[row.LineaSalida.alimento].Codigo
        try:
            informe[codigo_alimento][row.Beneficiario.tipobeneficiario] = \
                row[campo]
        except:
            print row.LineaSalida.alimento
        if row.Beneficiario.tipobeneficiario == 'OTROS BANCOS':
            query2 = query1 & (db.LineaSalida.alimento
                               == row.LineaSalida.alimento) \
                & (db.Beneficiario.tipobeneficiario == 'OTROS BANCOS') \
                & (db.CabeceraSalida.Beneficiario == db.Beneficiario.id)
            bancos = db(query2).select(db.Beneficiario.name)
            if len(bancos) > 1:
                informe[codigo_alimento]['sNombre'] = 'Varios'
            else:
                if bancos.first().name[:5] == 'BANCO':

                    informe[codigo_alimento]['sNombre'] = \
                        bancos.first().name[6:]
                else:
                    informe[codigo_alimento]['sNombre'] = \
                        'Varios'

    # calculo de beneficiarios

    bens = db(query1).select(db.Beneficiario.id,
                             db.Beneficiario.beneficiarios,
                             distinct=True)
    beneficiarios = sum([x['beneficiarios'] for x in bens.as_list()])
    informe['TOT']['bens'] = len(bens)
    informe['TOT']['beneficiarios'] = beneficiarios

    return informe

def escribe_detalle_albaran(id, fila, sheet, salidas, cell_style):
    linea = db.LineaSalida if salidas else db.LineaEntrada
    query = (linea.cabecera == id)
    lineas = db(query).select(linea.alimento, linea.Unidades)
    total = 0
    for linea in lineas:
        reg_alimento = db.Alimento[linea.alimento]
        alimento = "%s - %s" % (reg_alimento.Codigo, reg_alimento.Descripcion)
        sheet.write(fila, 2, alimento)
        sheet.write(fila, 3, linea.Unidades)
        total += linea.Unidades
        fila += 1
    sheet.write(fila, 4, total, cell_style)
    return fila + 2


def generar_albaran(mes, year, salidas=True):
    fecha1 = date(year, mes, 1)
    fecha2 = fecha1 + relativedelta.relativedelta(months=1)
    cabecera = db.CabeceraSalida if salidas else db.CabeceraEntrada
    usuario = db.CabeceraSalida.Beneficiario if salidas else db.CabeceraEntrada.Donante
    tabla_usuario = db.Beneficiario if salidas else db.Colaborador

    query = (cabecera.Fecha < fecha2) & (cabecera.Fecha >= fecha1)
    ezxf = xlwt.easyxf
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet(session.nombre_mes)
    data_xfs = [
        ezxf(num_format_str='#,##0'),
        ezxf(),
        ezxf(),
        ezxf(num_format_str='#,##0'),
        ezxf(num_format_str='#,##0'),
        ezxf(num_format_str='#,##0'),
        ezxf(num_format_str='#,##0'),
        ]

    style1 = \
        ezxf('font: name CG Times (WN), bold True, height 220;alignment: vertical center,horizontal center;border: top thin, left medium,right medium,bottom thin'
             )
    style2 = \
        ezxf('font: name CG Times (WN), bold True, height 160;alignment: vertical center,horizontal left;border: top dotted'
             )             
    style14 = \
        ezxf('font: name CG Times (WN), bold False, height 160;alignment: horizontal right,vertical center;border: top dotted, left thin,right thin,bottom dotted'
             )
    if salidas:
        mensaje = "Albaranes de Salida de %s de %s" % (session.nombre_mes, session.nombre_year)
    else:
        mensaje = "Albaranes de entrada de %s de %s" % (session.nombre_mes, session.nombre_year)
    albaranes = db(query).select(cabecera.id, cabecera.Fecha, usuario, orderby=cabecera.Fecha)
    
    sheet.write(0,0, mensaje, style1)
    sheet.write(0,4, "Totales", style1)

    fila = 1
    for albaran in albaranes:
        nombre_usuario = albaran[usuario].name
        sheet.write(fila, 0, nombre_usuario, style2)
        sheet.write(fila, 1, albaran.Fecha.strftime("%d/%m/%Y"), style2)
        fila +=1
        fila = escribe_detalle_albaran(albaran.id, fila, sheet, salidas, style2)


    # pie de hoja:
    fila +=1
    sheet.write(fila, 4, xlwt.Formula('SUM(E2:E' + str(fila) + ')'),
                style1)
    sheet.col(0).width =20000
    sheet.col(2).width = 15000
    s = cStringIO.StringIO()
    doc = CompoundDoc.XlsDoc()
    doc.save(s, book.get_biff_data())

    response.headers['Content-Type'] = 'application/vnd.ms-excel'
    response.headers['Content-Disposition'] = \
            'attachment; filename=Albaranes' + session.nombre_mes \
            + session.nombre_year + '.xls'
    return s.getvalue()


def datos_previos_albaran():
    nombre_mes = None
    nombre_year = None
    years = range(2013, date.today().year + 1)
    months = (
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio',
        'Julio',
        'Agosto',
        'Septiembre',
        'Octubre',
        'Noviembre',
        'Diciembre',
        )

    form = SQLFORM.factory(Field('year', label="Año",
                           requires=IS_IN_SET(years)), Field('mes',
                           requires=IS_IN_SET(months)),
                            buttons=[])
    fecha_pasada = date.today() - relativedelta.relativedelta(months=1)
    form.vars.year = fecha_pasada.year
    form.vars.mes = months[fecha_pasada.month - 1]
    return (form, months)

@auth.requires_login()
def albaranes_salida():
    form, months = datos_previos_albaran()
    if form.accepts(request, session):
        session.nombre_mes = form.vars.mes
        session.nombre_year = form.vars.year
        return generar_albaran(months.index(session.nombre_mes) + 1, int(session.nombre_year), salidas = True)
    return dict(form=form)

@auth.requires_login()
def albaranes_entrada():
    form, _ = datos_previos_albaran()
    if form.accepts(request, session):
        session.nombre_mes = form.vars.mes
        session.nombre_year = form.vars.year
        return generar_albaran(months.index(session.nombre_mes) + 1, int(session.nombre_year), salidas = False)
    return dict(form=form)


@auth.requires_login()
def descargar_albaranes():
    session.nombre_mes = request.vars.mes
    session.nombre_year = request.vars.year
    return dict()

@auth.requires_login()
def submit_albaran():
    salidas = request.vars.tipo == 'salida'
    _, months = datos_previos_albaran()
    fecha_pasada = date.today() - relativedelta.relativedelta(months=1)
    if not session.nombre_mes:
        session.nombre_mes = months[fecha_pasada.month - 1]
    if not session.nombre_year:
        session.nombre_year = str(fecha_pasada.year)

    return generar_albaran(months.index(session.nombre_mes) + 1, int(session.nombre_year), salidas = salidas)


@auth.requires_login()
def index():

    return locals()


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
