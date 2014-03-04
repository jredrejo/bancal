# -*- coding: utf-8 -*-
# apt-get install python-dateutil
from datetime import date
from dateutil import relativedelta
import locale
locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')

@auth.requires_login()
def mes():
    nombre_mes = None
    nombre_year = None
    tabla_informe = None
    years = range(2013, date.today().year + 1)
    months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
              "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")

    form = SQLFORM.factory(
        Field('year', label="Año", requires=IS_IN_SET(years)),
        Field('mes', requires=IS_IN_SET(months)),
        submit_button="Generar informe mensual"
    )
    fecha_pasada = date.today() - relativedelta.relativedelta(months=1)
    form.vars.year = fecha_pasada.year
    form.vars.mes = months[fecha_pasada.month - 1]

    if form.accepts(request, session):
        nombre_mes = form.vars.mes
        nombre_year = form.vars.year
        informe = generar_informe(
            months.index(nombre_mes) + 1, int(nombre_year))
        tabla_informe = generar_tabla(informe)

    elif form.errors:
        pass

    return dict(form=form, tabla_informe=tabla_informe, nombre_mes=nombre_mes, nombre_year=nombre_year)


@auth.requires_login()
def trimestre():
    years = range(2013, date.today().year + 1)
    trimestres = ("Primero", "Segundo", "Tercero", "Cuarto")

    form = SQLFORM.factory(
        Field('year', label="Año", requires=IS_IN_SET(years)),
        Field('trimestre', requires=IS_IN_SET(trimestres)),
        submit_button="Generar informe trimestral"
    )
    fecha_pasada = date.today() - relativedelta.relativedelta(months=3)
    form.vars.year = fecha_pasada.year
    form.vars.trimestre = trimestres[(fecha_pasada.month - 1) // 3]

    if form.accepts(request, session):
        session.year = form.vars.year
        session.month = form.vars.mes

    elif form.errors:
        pass

    return dict(form=form)


def quita_none(valor):
    if valor:
        return locale.format("%.2f",float(valor), grouping=True)
    else:
        return ' '

def quita_none_string(valor):
    if valor:
        return valor
    else:
        return ' '

def generar_tabla(informe):
    cabecera1 = (
        TH("CANTIDADES RECIBIDAS (KG)", _width="80%",
           _colspan="8", _class="informe"),
        TH("CANTID. SUMINISTRADAS (KG)", _width="20%", _colspan="3", _class="informe"))
    cabecera2 = (
        TH(" ", _class="informe2"), TH("ESTADO", _class="informe2"), TH("UE", _class="informe2"), TH(
            "INDUSTRIA", _class="informe2"), TH("DISTRIB.", _class="informe2"), TH("COLECTAS", _class="informe2"),
        TH("OTROS BANCOS", _colspan="2", _class="informe"), TH("OTROS BANCOS", _colspan="2", _class="informe"), TH("ASOCIACIONES", _class="informe2"))
    cabecera3 = (
        TH(" ", _class="informe3"), TH(" ", _class="informe3"), TH(" ", _class="informe3"), TH(" ",
                                                                   _class="informe3"), TH(" ", _class="informe3"),
        TH(" ", _class="informe3"), TH("Nombre", _class="informe"), TH("Cantidad", _class="informe"), TH("Nombre", _class="informe"), TH("Cantidad", _class="informe"), TH(" ", _class="informe3"))

    head = THEAD(TR(*cabecera1, _bgcolor="#A0A0A0"),
                 TR(*cabecera2, _bgcolor="#B0B0B0"),
                 TR(*cabecera3, _bgcolor="#B0B0B0"))
    filas = []
    codigos = informe.keys()
    i = 1
    for codigo in codigos:
        col = i % 2 and "#E3E3E3" or "#FFFFFF"
        col_clas = i % 2 and "even" or "odd"
        i += 1
        elemento = informe[codigo]
        if codigo == "TOT":
            pie = (
                TD(codigo, _class="pieinforme"),
                TD(quita_none(elemento["ESTADO"]), _class="pieinforme"),
                TD(quita_none(elemento["UNIÓN EUROPEA"]), _class="pieinforme"),
                TD(quita_none(elemento["INDUSTRIA"]), _class="pieinforme"),
                TD(quita_none(elemento["DISTRIBUCIÓN"]), _class="pieinforme"),
                TD(quita_none(elemento["COLECTAS"]), _class="pieinforme"),
                TD("", _class="pieinforme"),
                TD(quita_none(elemento["eCantidad"]), _class="pieinforme"),
                TD("", _class="pieinforme"),
                TD(quita_none(elemento["OTROS BANCOS"]), _class="pieinforme"),
                TD(quita_none(elemento["ASOCIACIONES"]), _class="pieinforme")
            )
        else:
            datos_elemento = (
                TD(codigo),
                TD(quita_none(elemento["ESTADO"])),
                TD(quita_none(elemento["UNIÓN EUROPEA"])),
                TD(quita_none(elemento["INDUSTRIA"])),
                TD(quita_none(elemento["DISTRIBUCIÓN"])),
                TD(quita_none(elemento["COLECTAS"])),
                TD(quita_none_string(elemento["eNombre"])),
                TD(quita_none(elemento["eCantidad"])),
                TD(quita_none_string(elemento["sNombre"])),
                TD(quita_none(elemento["OTROS BANCOS"])),
                TD(quita_none(elemento["ASOCIACIONES"])),
            )
            filas.append(TR(*datos_elemento, _bgcolor=col, _class=col_clas))

    body = TBODY(*filas)
    foot = TFOOT(TR(*pie))

    tabla = TABLE(*[head, body, foot], _border="1",
                  _align="center", _width="100%")
    return tabla


def generar_informe(mes, year):
    fecha1 = date(year, mes, 1)
    fecha2 = fecha1 + relativedelta.relativedelta(months=1)
    informe = {}
    fila_informe = {
        "ESTADO": None, "UNIÓN EUROPEA": None, "INDUSTRIA": None, "DISTRIBUCIÓN": None, "COLECTAS": None,
        "eNombre": None, "eCantidad": None, "sNombre": None, "OTROS BANCOS": None, "ASOCIACIONES": None}
    codigos = db(db.Alimento.Descripcion != None).select(
        db.Alimento.Codigo, orderby=db.Alimento.Codigo)
    for codigo in codigos:
        informe[codigo.Codigo] = {
            "ESTADO": None, "UNIÓN EUROPEA": None, "INDUSTRIA": None, "DISTRIBUCIÓN": None, "COLECTAS": None,
            "eNombre": None, "eCantidad": None, "sNombre": None, "OTROS BANCOS": None, "ASOCIACIONES": None}
    informe["TOT"] = fila_informe

    # ENTRADAS:
    campo = db.LineaEntrada.Unidades.sum()
    query = (db.CabeceraEntrada.Fecha < fecha2) & (
        db.CabeceraEntrada.Fecha >= fecha1)

    query1 = query & (db.LineaEntrada.cabecera == db.CabeceraEntrada.id)

    # totales:
    rows = db(query1).select(db.CabeceraEntrada.tipoProcedencia,
                             campo, groupby=db.CabeceraEntrada.tipoProcedencia)
    for row in rows:
        if row.CabeceraEntrada.tipoProcedencia != "OTROS BANCOS":
            informe["TOT"][row.CabeceraEntrada.tipoProcedencia] = row[campo]
        else:
            informe["TOT"]["eCantidad"] = row[campo]

    # por código:
    rows = db(
        query1).select(db.LineaEntrada.alimento, db.CabeceraEntrada.tipoProcedencia, campo,
                       groupby=(db.LineaEntrada.alimento, db.CabeceraEntrada.tipoProcedencia))
    for row in rows:
        if row.CabeceraEntrada.tipoProcedencia != "OTROS BANCOS":
            informe[row.LineaEntrada.alimento][
                row.CabeceraEntrada.tipoProcedencia] = row[campo]
        else:
            query2 = query1 & (db.LineaEntrada.alimento == row.LineaEntrada.alimento) & (
                db.CabeceraEntrada.tipoProcedencia == "OTROS BANCOS") & (db.CabeceraEntrada.Donante == db.Colaborador.id)
            bancos = db(query2).select(db.Colaborador.name)
            if len(bancos) > 1:
                informe[row.LineaEntrada.alimento]["eNombre"] = "Varios"
            else:
                informe[row.LineaEntrada.alimento][
                    "eNombre"] = bancos.first().name
                if informe[row.LineaEntrada.alimento]["eNombre"][:5] != "BANCO":
                    informe[row.LineaEntrada.alimento]["eNombre"] = "Varios"
            informe[row.LineaEntrada.alimento]["eCantidad"] = row[campo]

    # SALIDAS:
    campo = db.LineaSalida.Unidades.sum()
    query = (db.CabeceraSalida.Fecha < fecha2) & (
        db.CabeceraSalida.Fecha >= fecha1)
    query1 = query & (db.LineaSalida.cabecera == db.CabeceraSalida.id)
    query1 = query1 & (db.CabeceraSalida.Beneficiario == db.Beneficiario.id)
    # totales:
    rows = db(query1).select(db.Beneficiario.tipobeneficiario,
                             campo, groupby=db.Beneficiario.tipobeneficiario)
    for row in rows:
        informe["TOT"][row.Beneficiario.tipobeneficiario] = row[campo]

    # por codigo:
    rows = db(
        query1).select(db.LineaSalida.alimento, db.Beneficiario.tipobeneficiario,
                       campo, groupby=(db.LineaSalida.alimento, db.Beneficiario.tipobeneficiario))
    for row in rows:
        informe[row.LineaSalida.alimento][
            row.Beneficiario.tipobeneficiario] = row[campo]
        if row.Beneficiario.tipobeneficiario == "OTROS BANCOS":
            query2 = query1 & (db.LineaSalida.alimento == row.LineaSalida.alimento) & (
                db.Beneficiario.tipobeneficiario == "OTROS BANCOS") & (db.CabeceraSalida.Beneficiario == db.Beneficiario.id)
            bancos = db(query2).select(db.Beneficiario.name)
            if len(bancos) > 1:
                informe[row.LineaSalida.alimento]["sNombre"] = "Varios"
            else:
                informe[row.LineaSalida.alimento][
                    "sNombre"] = bancos.first().name
                if informe[row.LineaSalida.alimento]["sNombre"][:5] != "BANCO":
                    informe[row.LineaSalida.alimento]["sNombre"] = "Varios"

    return informe


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
