# -*- coding: utf-8 -*-
from gluon import *
import os

def rellena_provincias():
    import applications.bancal.modules.provincias
    listado=[]
    for prov in applications.bancal.modules.provincias.Provincias:
        listado.append({'tabla_id':int(prov[0]),'provincia': prov[1],'provinciaseo': prov[2], 'provincia3':prov[3],'postal':prov[4]})
    current.db.provincia.bulk_insert(listado)

def rellena_localidades():
    import applications.bancal.modules.localidades

    listado=[]
    for pobl in applications.bancal.modules.localidades.Localidades:
        datos_localidad={'provincia_id': pobl[1],'poblacion': pobl[2],'poblacionseo':pobl[3],'postal':pobl[4]}
        datos_localidad['latitud']=float(pobl[5])
        datos_localidad['longitud']=float(pobl[6])
        listado.append(datos_localidad)
    current.db.poblacion.bulk_insert(listado)
    
def rellena_paises():
    import applications.bancal.modules.paises

    listado=[]
    for pais in applications.bancal.modules.paises.Paises:
        datos_pais={'iso2': pais[1],'iso3': pais[2],'prefijo':pais[3],'pais':pais[4],'continente':pais[5],'subcontinente':pais[6]}
        datos_pais['iso_moneda']=pais[7]
        datos_pais['nombre_moneda']=pais[8]
        listado.append(datos_pais)
    current.db.pais.bulk_insert(listado)
    

def devuelve_datos(cadena):
    import sqlite3

    ruta = os.path.join(current.request.folder, "databases","SigabaAlimentos.sqlite")
    conn = sqlite3.connect(ruta)
    c = conn.cursor()
    r = c.execute(cadena)
    return r.fetchall()
        

def rellena_familias():
    datos = devuelve_datos(r"select idFamilia,Descripcion     from Familia")
    listado = []
    for dato in datos:
        listado.append({'id':dato[0],'Descripcion':dato[1]})
    
    current.db.Familia.bulk_insert(listado)
    
def rellena_subfamilias():
    datos = devuelve_datos(r"select idSubFamilia,Descripcion,idFamilia from Subfamilia")
    listado = []
    for dato in datos:
        listado.append({'id':dato[0],'Descripcion':dato[1],'Familia':dato[2]})

    current.db.SubFamilia.bulk_insert(listado)

def rellena_alimentos():
    datos = devuelve_datos(r"select  idAlimento,CODIGO,Descripcion, idSubFamilia,idFamilia,idConservacion,idUnidad from Alimento")
    listado = []
    for dato in datos:
        alimento={'id':dato[0],'Codigo':int(dato[1]), 'Descripcion':dato[2],'Familia':dato[4],'SubFamilia':dato[3]}
        if dato[5]==1:
            alimento['Conservacion']='Frío'
        if dato[6] == 2:
            alimento['Unidades']='L.'
            
        listado.append(alimento)

    current.db.Alimento.bulk_insert(listado)        
