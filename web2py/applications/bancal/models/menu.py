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

# Para el autocompletado con aptana/eclipse+pydev:
if 0:
    from gluon import *
    (request, session, response, T, cache) = (current.request,
                                              current.session, current.response, current.t, current.cache)
    from gluon.dal import DAL
    from gluon.sqlhtml import *
    from gluon.validators import *


response.logo = A(B('Banco de Alimentos'), XML('&nbsp;Badajoz'),
                  _class="brand", _href=URL('default', 'index'))
response.title = 'Banco de alimentos'
response.subtitle = 'Badajoz'

# read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'José L. Redrejo Rodríguez <jredrejo@itais.net>'
response.meta.description = 'Gestión de Banco de Alimentos'
response.meta.keywords = 'banco alimentos, banco, alimentos, caritas'
response.meta.generator = None

# your http://google.com/analytics id
response.google_analytics_id = None

if session.auth:
    response.menu = [
        (T('Configuración'), False, None, [
            (T('Datos de la sede'), False, URL('config', 'sede'), []),
            (T('Almacenes'), False, URL('config', 'almacen'), []),
            (T('Alimentos'), False, URL('config', 'alimentos'), []),
            (T('Cierre Almacén'), False, URL('config', 'cierre'), []),
        ])
    ]

    response.menu += [(T('Colaboradores'), False, URL('colaboradores', 'index'), [
        (T('Donantes'), False,  URL('colaboradores', 'donantes'), []),
        (T('Voluntarios'), False, URL('colaboradores', 'voluntarios'), []),
        (T('Patrocinadores'), False, URL('colaboradores', 'patrocinadores'), []),
        (T('Socios'), False, URL('colaboradores', 'socios'), [])

    ])]

    response.menu += [(T('Beneficiarios'), False, URL('beneficiarios', 'index'), [])]

    response.menu += [(T('Almacen'), False, URL('almacen', 'stock'), [
        (T('Entradas'), False, URL('almacen', 'entradas'), []),
        (T('Nueva Entrada'), False, URL('almacen', 'nueva_entrada'), []),
        (LI(_class='divider'), False, None, []),
        (T('Salidas'), False, URL('almacen', 'salidas'), []),
        (T('Nueva Salida'), False, URL('almacen', 'nueva_salida'), []),
    ])]

    response.menu += [(T('Informes'), False, None, [
        (T('Movimientos Mensuales'), False, URL('informes', 'mes'), []),
        (T('Informe trimestral'), False, URL('informes', 'trimestre'), []),

    ])]

    # (T('Incidencias'), False,  URL('almacen', 'incidencias'), [])])]

else:
    response.menu = []
