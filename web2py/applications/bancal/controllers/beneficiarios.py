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

@auth.requires_login()
def index():
    import ui_def
    ui = ui_def.uidict()

    search_text = request.get_vars.search_text
    query = search_query(db.Beneficiario.id, search_text,
                         [db.Beneficiario.name])

    grid = SQLFORM.grid(
        query,
        ui=ui,
        search_widget=search_form,
        maxtextlength=40,
        fields=[
            db.Beneficiario.name,
            db.Beneficiario.poblacion,
            db.Beneficiario.telefono,
            db.Beneficiario.movil,
            db.Beneficiario.contacto,
            db.Beneficiario.tipobeneficiario,
            ],
        orderby=~db.Beneficiario.id,
        )

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
