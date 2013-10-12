# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('Banco de Alimentos'),XML('&nbsp;Badajoz'),
                  _class="brand",_href=URL('default', 'index'))
response.title ='Banco de alimentos'
response.subtitle = 'Badajoz'

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'José L. Redrejo Rodríguez <jredrejo@itais.net>'
response.meta.description = 'Gestión de Banco de Alimentos'
response.meta.keywords = 'banco alimentos, banco, alimentos, caritas'
response.meta.generator = None

## your http://google.com/analytics id
response.google_analytics_id = None

if session.auth:
    response.menu = [
        (T('Configuración'), False, None, [
        (T('Datos de la sede'), False,  URL('config', 'sede'), []),
        (T('Almacenes'), False,  URL('config', 'almacen'), []),
        (T('Alimentos'), False,  URL('config', 'alimentos'), []),
        ])
    ]



    response.menu += [(T('Colaboradores'), False, None, [
                    (T('Donantes'), False,  URL('default', 'index'), []),
                    (T('Beneficiarios'), False,  URL('default', 'index'), []),
                    (T('Voluntarios'), False,  URL('default', 'index'), []),
                    (T('Patrocinadores'), False,  URL('default', 'index'), [])

                    ])]

    response.menu +=[(T('Almacen'), False, None, [
                    (T('Entradas'), False,  URL('default', 'index'), []),
                    (T('Salidas'), False,  URL('default', 'index'), []),
                    (T('Stock'), False,  URL('default', 'index'), [])])]

else:
    response.menu = []

if "auth" in locals(): auth.wikimenu()
