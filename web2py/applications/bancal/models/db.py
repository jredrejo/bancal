# -*- coding: utf-8 -*-

#
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
#

# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# request.requires_https()
from gluon import current

db = DAL('sqlite://storage.sqlite', pool_size=1, check_reserved=['all'])
current.db = db

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
# (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
#

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

# create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

# configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

# configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True


#
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable',Field('myfield','string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
# 'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
#


db.define_table('Familia',
                Field('Descripcion', label='Descripción'), format='%(Descripcion)s'
                )

db.define_table('SubFamilia',
                Field('Descripcion', label='Descripción'),
                Field('Familia', db.Familia),
                format='%(Descripcion)s'
                )

db.define_table('Alimento',
                Field('Codigo', 'integer', label='Código'),
                Field('Descripcion', label='Descripción'),
                Field('Familia', db.Familia),
                Field('SubFamilia', db.SubFamilia),
                Field('Conservacion', label='Conservación', default=T(
                    'Calor')),
                Field('Unidades', default='Kg.')
                )
db.Alimento.Conservacion.requires = IS_IN_SET((T('Calor'), T('Frío')))
db.Alimento.Unidades.requires = IS_IN_SET(('Kg.', 'L.'))

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

# Lista de paises, obtenida de http://dmnet.bitacoras.com/archivos/inclasificable/lista-de-paises-en-sql.php
#
# id: ID numérico según la ISO 3166-1 y la División Estadística de las Naciones Unidas
# iso2: código de dos letras según la ISO 3166-1
# iso3: código de tres letras según la ISO 3166-1
# prefijo: prefijo telefónico según la recomendación E.164
# nombre: nombre completo en español
# continente: nombre del continente en español
# subcontinente: nombre del subcontinente en español (para diferenciar América del Sur/Central/Norte/Caribe)
# iso_moneda: código de tres letras de su moneda según la ISO 4217
# nombre_moneda: nombre de la moneda en español

db.define_table('pais',
                Field('iso2', 'string', length=2, unique=True, notnull=True),
                Field('iso3', 'string', length=3, unique=True, notnull=True),
                Field('prefijo', 'string', length=5, notnull=True),
                Field('pais', notnull=True, label='País'),
                Field('continente', 'string', length=16),
                Field('subcontinente', 'string', length=32),
                Field('iso_moneda', 'string', length=3),
                Field('nombre_moneda', label='Moneda'),
                format='%(pais)s'

                )

db.define_table('provincia',
                Field('provincia',  notnull=True, unique=True),
                Field('provinciaseo', notnull=True, unique=True),
                Field('postal', 'string', length=2, notnull=True, unique=True),
                Field('provincia3', 'string',
                      length=3, notnull=True, unique=True),
                Field('tabla_id', 'integer'),
                format='%(provincia)s'

                )


db.define_table('poblacion',
                Field('provincia_id', db.provincia, label='Provincia'),
                Field('poblacion',  notnull=True,
                      unique=False, label='Nombre localidad'),
                Field('poblacionseo', notnull=False,
                      unique=True, readable=False, writable=False),
                Field('postal', 'string', length=5,
                      notnull=False, default=None, label='Cód. Postal'),
                Field('latitud', 'decimal(9,6)', notnull=False,
                      default=None, label='Latitud (Coord)'),
                Field('longitud', 'decimal(9,6)', notnull=False,
                      default=None, label='Longitud (Coord)'),
                format='%(poblacion)s'


                )
db.poblacion.postal.requires = IS_EMPTY_OR(IS_MATCH(
    '^\d{5}(-\d{4})?$', error_message='El Código Postal deben ser 5 dígitos'))
db.poblacion.provincia_id.requires = IS_IN_DB(
    db, 'provincia.tabla_id', 'provincia.provincia', error_message='Debe asignar una provincia')


#
def ajax_autocomplete(f, v):
    get_url = URL(r=request, f='get_items')
    wrapper = DIV()
    inp = SQLFORM.widgets.string.widget(f, v)
    wrapper.append(inp)
    return wrapper


db.define_table('Sede',
                Field('name', label='Nombre'),
                Field('provincia', label='Provincia', default='Badajoz'),
                Field('poblacion', label='Población', default='Badajoz'),
                Field('direccion', label="Dirección", length=200,
                      default="Ctra. Campomayor - Polígono Industrial El Nevero"),
                Field('postal', label="Cód. Postal", length=5, default='06006'),
    Field('CIF'),
    Field('telefono', label='Teléfono 1', default='924259803'),
    Field('telefono2', label='Teléfono 2', default='924259206'),
    Field('movil', label='Móvil'),
    Field('email', label='Correo electrónico',
          default='badajoz@bancodealimentos.info'),
    Field('cuenta', label='Cuenta bancaria'),
    format='%(name)s'
    )
db.Sede.id.readable = False
db.Sede.postal.requires = IS_EMPTY_OR(IS_MATCH(
    '^\d{5}(-\d{4})?$', error_message='El Código Postal deben ser 5 dígitos'))
db.Sede.email.requires = IS_EMPTY_OR(IS_EMAIL(
    error_message=auth.messages.invalid_email))
db.Sede.provincia.widget = ajax_autocomplete
db.Sede.poblacion.widget = ajax_autocomplete

db.define_table('Almacen',
    Field('name', label='Nombre', default='El Nevero'),
    Field('sede', db.Sede, label='Sede', default=1)
    )

tipo_beneficiario = (
    "TODOS", "Residencia de Ancianos", "Guarderias", "Comedores Sociales", "Caritas",
                    "Centros de Reinserción", "Centros de Acogida", "Conventos", "Asociaciones Asistenciales",
                    "Banco Alimentos", "Regularizacion de existencias", "Iglesias Evangelistas", "Ayuntamientos",
                    "Otras Asociaciones", "Otras Confesiones Religiosas", "Otros Organismos Publicos")
tipo_empresa = (
    "ACTUALIZACIÓN DE STOCK", "MAYORISTAS Y DISTRIBUIDUIDORES", "EMPRESAS E INDUSTRIA AGROALIMENTARIA",
              "BANCO DE ALIMENTOS", "ASOC. BENEF./SOCIAL/DEPORT./CULTUR.", "CENTROS EDUCATIVOS", "COMERCIOS MINORISTAS",
              "DONACIONES PARTICULARES", "ORGANISMOS PÚBLICOS", "FEGA")
tipo_procedencia = (
    "REGULARIZACIÓN DE STOCK", "DONACIONES", "OPERACIÓN KILO", "MERMAS", "EXCEDENTES DE PRODUCCIÓN",
                  "DECOMISOS", "AYUDAS PÚBLICAS", "INVENTARIO", "OTROS BANCOS", "UNION EUROPEA")
grupo_recogida = ("PRIMER DÍA", "SEGUNDO DÍA",
                  "TERCER DÍA", "CUARTO DÍA", "QUINTO DÍA")
tipo_colaboracion = ("Miembro del equipo directivo",
                     "Voluntario en banco", "Otro modo de voluntariado")

db.define_table('Colaborador',
    Field('name', label='Nombre'),
    Field('provincia', label='Provincia', default='Badajoz'),
    Field('poblacion', label='Población', default='Badajoz'),
    Field('direccion', label="Dirección", length=200,
          default="Ctra. Campomayor - Polígono Industrial El Nevero"),
    Field('postal', label="Cód. Postal", length=5, default='06006'),
    Field('nif', label="CIF/NIF"),
    Field('telefono', label='Teléfono 1', default='924259803'),
    Field('telefono2', label='Teléfono 2', default='924259206'),
    Field('movil', label='Móvil'),
    Field('email', label='Correo electrónico',
          default='badajoz@bancodealimentos.info'),
    Field('cuenta', label='Cuenta bancaria'),


    )
db.Colaborador.id.readable = False
db.Colaborador.postal.requires = IS_EMPTY_OR(IS_MATCH(
    '^\d{5}(-\d{4})?$', error_message='El Código Postal deben ser 5 dígitos'))
db.Colaborador.email.requires = IS_EMPTY_OR(
    IS_EMAIL(error_message=auth.messages.invalid_email))
db.Colaborador.provincia.widget = ajax_autocomplete
db.Colaborador.poblacion.widget = ajax_autocomplete
