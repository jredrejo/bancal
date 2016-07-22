# -*- coding: utf-8 -*-
##############################################################################
# Project:     Bancal - Gestión de almacén para los Bancos de Alimentos
# Language:    Python 2.7
# Date:        15-Ago-2013.
# Ver.:        20-Jul-2017.
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
"""Module to create a test db.
It only makes sense if used via py.test, from the web2py folder, i.e.
py.test applications/bancal/tests/

"""
from gluon import current


def rellena_provincias():
    import provincias
    listado = []
    for prov in provincias.Provincias:
        listado.append({
            'tabla_id': int(prov[0]),
            'provincia': prov[1],
            'provinciaseo': prov[2],
            'provincia3': prov[3],
            'postal': prov[4],
        })
    current.db.provincia.bulk_insert(listado)


def rellena_localidades():
    import localidades

    listado = []
    for pobl in localidades.Localidades:
        datos_localidad = {
            'provincia_id': pobl[1],
            'poblacion': pobl[2],
            'poblacionseo': pobl[3],
            'postal': pobl[4],
        }
        datos_localidad['latitud'] = float(pobl[5])
        datos_localidad['longitud'] = float(pobl[6])
        listado.append(datos_localidad)
    current.db.poblacion.bulk_insert(listado)


def rellena_paises():
    import paises
    listado = []
    for pais in paises.Paises:
        datos_pais = {
            'iso2': pais[1],
            'iso3': pais[2],
            'prefijo': pais[3],
            'pais': pais[4],
            'continente': pais[5],
            'subcontinente': pais[6],
        }
        datos_pais['iso_moneda'] = pais[7]
        datos_pais['nombre_moneda'] = pais[8]
        listado.append(datos_pais)
    current.db.pais.bulk_insert(listado)


def rellena_alimentos():
    import alimentos

    listado = []
    for alimento in alimentos.Alimentos:
        datos_alimento = {'id': alimento[0],
                          'Codigo': alimento[1],
                          'Descripcion': alimento[2],
                          'Conservacion': alimento[5],
                          'Unidades': alimento[6]
                          }
        listado.append(datos_alimento)
    current.db.Alimento.bulk_insert(listado)


def crea_usuario():
    from gluon.validators import CRYPT
    from gluon.tools import Auth
    db = current.db
    auth = Auth(db)

    db.Sede.insert(name="Sede de pruebas")
    db.Almacen.insert(name="AlmacenTest 1")
    db.Almacen.insert(name="AlmacenTest 2")
    my_crypt = CRYPT(key=auth.settings.hmac_key)
    crypted_passwd = my_crypt('password_malo')[0]
    db.commit()
    db.auth_user.insert(email='admin@admin.com', first_name='Administrator', password=crypted_passwd)
    auth.add_group('admins', 'Administradores de la aplicación')
    auth.add_membership(1, 1)
    auth.add_permission(1, 'admins', db.auth_user)

    db.Beneficiario.insert(name="Beneficiario 1", tipobeneficiario="ASOCIACIONES")
    db.Colaborador.insert(name="Donante 1", Donante=True)
    db.commit()

def cleanup_db():
    db = current.db
    db.rollback()
    for tab in db.tables:
        db[tab].truncate()
    db.commit()


def fill_tables(db):
    current.db = db
    cleanup_db()
    crea_usuario()
    rellena_paises()
    rellena_provincias()
    rellena_localidades()
    rellena_alimentos()
    current.db.commit()
