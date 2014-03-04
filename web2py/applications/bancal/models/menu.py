# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#
# Customize your APP title, subtitle and menus here
#

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
        (T('Datos de la sede'), False,  URL('config', 'sede'), []),
        (T('Almacenes'), False,  URL('config', 'almacen'), []),
        (T('Alimentos'), False,  URL('config', 'alimentos'), []),
        ])
    ]

    response.menu += [(T('Colaboradores'), False,URL('colaboradores','index'), [
        (T('Donantes'), False,  URL('colaboradores', 'donantes'), []),        
        (T('Voluntarios'), False,  URL('colaboradores', 'voluntarios'), []),
        (T('Patrocinadores'), False,  URL('colaboradores', 'patrocinadores'), []),
        (T('Socios'), False,  URL('colaboradores', 'socios'), [])

    ])]

    response.menu += [(T('Beneficiarios'),False, URL('beneficiarios','index'),[])]

    response.menu += [(T('Almacen'), False,  URL('almacen', 'stock'), [
        (T('Entradas'), False,  URL('almacen', 'entradas'), []),
        (T('Nueva Entrada'), False,  URL('almacen', 'nueva_entrada'), []),
        (LI(  _class='divider'),False, None,[]),
        (T('Salidas'), False,  URL('almacen', 'salidas'), []),
        (T('Nueva Salida'), False,  URL('almacen', 'nueva_salida'), []),
        ])]


    response.menu += [(T('Informes'), False,  None, [
        (T('Movimientos Mensuales'), False,  URL('informes', 'mes'), []),
        (T('Informe trimestral'), False,  URL('informes', 'trimestre'), []),

        ])]


        #(T('Incidencias'), False,  URL('almacen', 'incidencias'), [])])]

else:
    response.menu = []

if "auth" in locals():
    auth.wikimenu()
