#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
# Project:     Bancal - Gestión de almacén para los Bancos de Alimentos
# Language:    Python 2.7
# Date:        15-Ago-2013.
# Ver.:        22-Jul-2014.
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
"""Módulo de importación de tablas desde la base de datos antigua.
Una vez hechas las importaciones ya no se usa"""

from gluon import *
import os
import datetime


def rellena_provincias():
    import applications.bancal.modules.provincias
    listado = []
    for prov in applications.bancal.modules.provincias.Provincias:
        listado.append({
            'tabla_id': int(prov[0]),
            'provincia': prov[1],
            'provinciaseo': prov[2],
            'provincia3': prov[3],
            'postal': prov[4],
        })
    current.db.provincia.bulk_insert(listado)


def rellena_localidades():
    import applications.bancal.modules.localidades

    listado = []
    for pobl in applications.bancal.modules.localidades.Localidades:
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
    import applications.bancal.modules.paises

    listado = []
    for pais in applications.bancal.modules.paises.Paises:
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


def rellena_alimentos2():
    import applications.bancal.modules.alimentos

    listado = []
    for alimento in applications.bancal.modules.alimentos.Alimentos:
        datos_alimento = {'Codigo': alimento[0],
                          'Descripcion': alimento[1]}
        listado.append(datos_alimento)
    current.db.Alimento.bulk_insert(listado)


def devuelve_datos(cadena, archivo='SigabaAlimentos.sqlite'):
    import sqlite3

    ruta = os.path.join(current.request.folder, 'databases', archivo)
    conn = sqlite3.connect(ruta)
    c = conn.cursor()
    r = c.execute(cadena)
    return r.fetchall()


def rellena_familias():
    datos = \
        devuelve_datos(r"select idFamilia,Descripcion     from Familia")
    listado = []
    for dato in datos:
        listado.append({'id': dato[0], 'Descripcion': dato[1]})

    current.db.Familia.bulk_insert(listado)


def rellena_subfamilias():
    datos = \
        devuelve_datos(r"select idSubFamilia,Descripcion,idFamilia from Subfamilia"
                       )
    listado = []
    for dato in datos:
        listado.append({'id': dato[0], 'Descripcion': dato[1],
                       'Familia': dato[2]})

    current.db.SubFamilia.bulk_insert(listado)


def rellena_alimentos():
    datos = \
        devuelve_datos(r"select  idAlimento,CODIGO,Descripcion, idSubFamilia,idFamilia,idConservacion,idUnidad from Alimento"
                       )
    listado = []
    for dato in datos:
        alimento = {
            'id': dato[0],
            'Codigo': int(dato[1]),
            'Descripcion': dato[2],
            'Familia': dato[4],
            'SubFamilia': dato[3],
        }
        if dato[5] == 1:
            alimento['Conservacion'] = 'Frío'
        if dato[6] == 2:
            alimento['Unidades'] = 'L.'

        listado.append(alimento)

    current.db.Alimento.bulk_insert(listado)


def rellena_estanterias():
    datos = \
        devuelve_datos(r"select  idEstanteria,Descripcion from Estanteria"
                       , 'SigabaCliente.sqlite')
    listado = []
    for dato in datos:
        estante = {'id': dato[0], 'name': dato[1]}
        listado.append(estante)

    current.db.Estanteria.bulk_insert(listado)


def rellena_cabecerasalmacen():

    datos = \
        devuelve_datos(r"select  idCabecera,idAlimento from AlmacenCabecera"
                       , 'SigabaCliente.sqlite')
    listado = []
    for dato in datos:
        estante = {'id': dato[0], 'alimento': dato[1]}
        listado.append(estante)

    current.db.CabeceraAlmacen.bulk_insert(listado)


def rellena_lineasalmacen():

    datos = \
        devuelve_datos(r"select  idAlmacenCabecera,idAlmacenLinea,Unidadesiniciales,UnidadesStock,FechaCaducidad,NombreLote,idEstanteria,PesoUnidad,NumPalet from AlmacenLinea"
                       , 'SigabaCliente.sqlite')
    listado = []
    for dato in datos:
        linea = {
            'id': dato[1],
            'cabecera': dato[0],
            'Stock': float(dato[3]),
            'stockinicial': float(dato[2]),
            'Lote': dato[5],
            'estanteria': dato[6],
            'PesoUnidad': float(dato[7]),
            'Palets': dato[8],
            }
        linea['Caducidad'] = datetime.datetime.strptime((dato[4])[:10],
                '%Y-%m-%d').date()

        listado.append(linea)

    current.db.LineaAlmacen.bulk_insert(listado)


def xstr(s):
    return (None if s == '' else str(s))


def rellena_colaboradores():
    mysql = \
        'select idColaborador,Nombre,Apellido1,Apellido2,Telefono,FAX,Movil,EMail,NombreContacto,'
    mysql += \
        'Socio,Voluntario,Donante,Patrocinador,Voluntario.FechaAlta,Nif,Direccion,PROVINCIA,MUNICIPIO,'
    mysql += \
        'CodigoPostal from Colaborador inner join Domicilio on Colaborador.idDomicilio=Domicilio.idDomicilio '
    mysql += \
        'inner join Voluntario on Colaborador.idColaborador=Voluntario.idVoluntario'

    datos = devuelve_datos(mysql, 'SigabaCliente.sqlite')

    listado = []
    for dato in datos:
        colaborador = {}
        for (ind, item) in enumerate([
            'id',
            'name',
            'apellido1',
            'apellido2',
            'telefono',
            'telefono2',
            'movil',
            'email',
            'contacto',
            ]):
            if dato[ind] != '':
                colaborador[item] = dato[ind]
        for (ind, item) in enumerate(['nif', 'direccion', 'provincia',
                'poblacion', 'postal']):
            if dato[ind + 14] != '':
                colaborador[item] = dato[ind + 14]
        for (ind, item) in enumerate(['Socio', 'Voluntario', 'Donante',
                'Patrocinador']):
            if dato[ind + 9] == 1:
                colaborador[item] = True
        if dato[13]:
            colaborador['fechalta'] = \
                datetime.datetime.strptime((dato[13])[:10], '%Y-%m-%d'
                    ).date()

        listado.append(colaborador)
    current.db.Colaborador.bulk_insert(listado)


def rellena_beneficiarios():
    mysql = \
        'select idBeneficiario,Nombre,Apellido1,Apellido2,Telefono,FAX,Movil,EMail,NombreContacto,'
    mysql += \
        'CIF,Direccion,PROVINCIA,MUNICIPIO,CodigoPostal,Faga,TelefonoBeneficiario,idGrupoRecogida,'
    mysql += \
        'idTipoBeneficiario from Beneficiario inner join Domicilio '
    mysql += 'on Beneficiario.idDomicilio=Domicilio.idDomicilio '

    datos = devuelve_datos(mysql, 'SigabaCliente.sqlite')
    tipo_beneficiario = (
        'TODOS',
        'Residencia de Ancianos',
        'Guarderias',
        'Comedores Sociales',
        'Caritas',
        "Centros de Reinserción",
        'Centros de Acogida',
        'Conventos',
        'Asociaciones Asistenciales',
        'Banco Alimentos',
        'Regularizacion de existencias',
        'Iglesias Evangelistas',
        'Ayuntamientos',
        'Otras Asociaciones',
        'Otras Confesiones Religiosas',
        'Otros Organismos Publicos',
        )

    grupo_recogida = {
        0: None,
        1: "PRIMER DÍA",
        3: "SEGUNDO DÍA",
        4: "TERCER DÍA",
        5: "CUARTO DÍA",
        6: "QUINTO DÍA",
        }
    listado = []
    for dato in datos:
        beneficiario = {}
        for (ind, item) in enumerate([
            'id',
            'name',
            'apellido1',
            'apellido2',
            'telefono',
            'telefono2',
            'movil',
            'email',
            'contacto',
            'nif',
            'direccion',
            'provincia',
            'poblacion',
            'postal',
            ]):
            if dato[ind] != '':
                beneficiario[item] = dato[ind]
            if dato[14] == 1:
                beneficiario['FAGA'] = True
            if dato[15] != '':
                beneficiario['telefono'] = dato[15]
            if dato[16] > 0:
                beneficiario['gruporecogida'] = grupo_recogida[dato[16]]
            beneficiario['tipobeneficiario'] = \
                tipo_beneficiario[dato[17]]

        listado.append(beneficiario)
    current.db.Beneficiario.bulk_insert(listado)


def rellena_cabecerasentradas():
    tipo_procedencia = {
        0: "REGULARIZACIÓN DE STOCK",
        1: 'DONACIONES',
        2: "OPERACIÓN KILO",
        3: 'MERMAS',
        4: "EXCEDENTES DE PRODUCCIÓN",
        5: 'DECOMISOS',
        6: "AYUDAS PÚBLICAS",
        7: 'INVENTARIO',
        8: 'OTROS BANCOS',
        9: 'UNION EUROPEA',
        }

    datos = \
        devuelve_datos(r"select  idEntradaCabecera,idTipoProcedencia,idDonante,FechaEntrada from EntradaCabecera"
                       , 'SigabaCliente.sqlite')
    listado = []
    for dato in datos:
        estante = {'id': dato[0], 'Donante': dato[2]}
        estante['Fecha'] = datetime.datetime.strptime((dato[3])[:10],
                '%Y-%m-%d').date()
        if dato[1]:
            estante['tipoProcedencia'] = tipo_procedencia[int(dato[1])]
        listado.append(estante)

    current.db.CabeceraEntrada.bulk_insert(listado)


def rellena_lineasentradas():

    datos = \
        devuelve_datos(r"select IdEntradaLinea,idEntradaCabecera,idAlimento,NumUnidades,PesoUnidad,FechaCaducidad,NOMBRELOTE,idEstanteria,idAlmacenLinea,preciokg from EntradaLinea"
                       , 'SigabaCliente.sqlite')
    listado = []
    for dato in datos:
        estante = {
            'id': dato[0],
            'cabecera': dato[1],
            'alimento': dato[2],
            'Unidades': float(dato[3]),
            'PesoUnidad': float(dato[4]),
            'Lote': dato[6],
            'estanteria': dato[7],
            'LineaAlmacen': dato[8],
            'PrecioKg': float(dato[9]),
            }
        estante['Caducidad'] = \
            datetime.datetime.strptime((dato[5])[:10], '%Y-%m-%d'
                ).date()

        listado.append(estante)

    current.db.LineaEntrada.bulk_insert(listado)


def rellena_cabecerasalidas():
    datos = \
        devuelve_datos(r"select IdSalidaCabecera,idBeneficiario,FechaSalida from SalidaCabecera"
                       , 'SigabaCliente.sqlite')
    listado = []
    for dato in datos:
        estante = {'id': dato[0], 'Beneficiario': dato[1]}
        estante['Fecha'] = datetime.datetime.strptime((dato[2])[:10],
                '%Y-%m-%d').date()
        listado.append(estante)

    current.db.CabeceraSalida.bulk_insert(listado)


def rellena_lineasalidas():

    datos = \
        devuelve_datos(r"select IdSalidaLinea,idSalidaCabecera,idAlimento,NumUnidades,PesoUnidad,FechaCaducidad,NOMBRELOTE,idEstanteria,idAlmacenLinea,preciokg from SalidaLinea"
                       , 'SigabaCliente.sqlite')
    listado = []
    for dato in datos:
        estante = {
            'id': dato[0],
            'cabecera': dato[1],
            'alimento': dato[2],
            'Unidades': float(dato[3]),
            'PesoUnidad': float(dato[4]),
            'Lote': dato[6],
            'estanteria': dato[7],
            'LineaAlmacen': dato[8],
            'PrecioKg': float(dato[9]),
            }
        estante['Caducidad'] = \
            datetime.datetime.strptime((dato[5])[:10], '%Y-%m-%d'
                ).date()

        listado.append(estante)

    current.db.LineaSalida.bulk_insert(listado)
