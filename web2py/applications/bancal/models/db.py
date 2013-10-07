# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()


db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])


## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True


#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################


db.define_table('Almacen',
    Field('Descripcion',label='Descripción'),
    Field('Direccion', label='Dirección'),
    Field('Activo','boolean',default=True)
    )

db.define_table('Familia',
    Field('Descripcion',label='Descripción')
    )

db.define_table('SubFamilia',
    Field('Descripcion',label='Descripción'),
    Field('Familia',db.Familia)
    )

db.define_table('Alimento',
    Field('Codigo','integer',label='Código'),
    Field('Descripcion',label='Descripción'),
    Field('Familia',db.Familia),
    Field('SubFamilia',db.SubFamilia),
    Field('Conservacion',label='Conservación',default=T('Calor')),
    Field('Unidades',default='Kg.')
    )
db.Alimento.Conservacion.requires=IS_IN_SET(T('Calor'),T('Frío'))
db.Alimento.Unidades.requires=IS_IN_SET('Kg.','L.')    
## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
