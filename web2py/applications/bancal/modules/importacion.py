# -*- coding: utf-8 -*-
from gluon import *
def rellena_provincias():
    import applications.cursillos.modules.provincias
    listado=[]
    for prov in applications.cursillos.modules.provincias.Provincias:
        listado.append({'tabla_id':int(prov[0]),'provincia': prov[1],'provinciaseo': prov[2], 'provincia3':prov[3],'postal':prov[4]})
    db.provincia.bulk_insert(listado)

def rellena_localidades():
    import applications.cursillos.modules.localidades

    listado=[]
    for pobl in applications.cursillos.modules.localidades.Localidades:
        datos_localidad={'provincia_id': pobl[1],'poblacion': pobl[2],'poblacionseo':pobl[3],'postal':pobl[4]}
        datos_localidad['latitud']=float(pobl[5])
        datos_localidad['longitud']=float(pobl[6])
        listado.append(datos_localidad)
    db.poblacion.bulk_insert(listado)
    
def rellena_paises():
    import applications.cursillos.modules.paises

    listado=[]
    for pais in applications.cursillos.modules.paises.Paises:
        datos_pais={'iso2': pais[1],'iso3': pais[2],'prefijo':pais[3],'pais':pais[4],'continente':pais[5],'subcontinente':pais[6]}
        datos_pais['iso_moneda']=pais[7]
        datos_pais['nombre_moneda']=pais[8]
        listado.append(datos_pais)
    db.pais.bulk_insert(listado)
    
def rellena_familias():
    db2= DAL('sqlite://SigabaAlimentos.sqlite',auto_import=True)
    listado =[]
    import pdb
    pdb.set_trace()
    
        
