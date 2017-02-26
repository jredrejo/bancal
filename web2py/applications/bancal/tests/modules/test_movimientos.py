#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

@pytest.fixture(scope="module")
def insertar_entrada(web2py):
    from applications.bancal.modules.movimientos import nueva_lineaalmacen
    from collections import namedtuple
    db = web2py.db

    entrada_id = db.CabeceraEntrada.insert(tipoProcedencia="DISTRIBUCIÓN", Donante=1)
    alimento_id = db(db.Alimento.Descripcion != '').select().first().id
    Storage = namedtuple('Storage', 'alimento Caducidad PesoUnidad estanteria Lote Unidades')
    nuevo_alimento = Storage(alimento=alimento_id, Caducidad='31-12-1999', PesoUnidad=1.0, estanteria=1, Lote=None, Unidades=100.0)
    nueva_lineaalmacen(nuevo_alimento, True)
    db.LineaEntrada.insert(cabecera=entrada_id, alimento=alimento_id, Unidades=100)
    db.commit()


def test_insertar_salida(web2py):
    from applications.bancal.modules.movimientos import ultima_salida, insertar_salida
    import datetime
    db = web2py.db
    salida_previa = ultima_salida()
    salida1 = insertar_salida(beneficiario_id=1, fecha=datetime.datetime.now())
    assert salida1 == salida_previa +1


def test_insertar_linea_salida(web2py, insertar_entrada):
    from applications.bancal.modules.movimientos import insertar_linea_salida, stock_alimento, insertar_salida, borrar_linea
    import datetime
    db = web2py.db
    salida1 = insertar_salida(beneficiario_id=1, fecha=datetime.datetime.now())
    alimento_id = db(db.Alimento.Descripcion != '').select().first().id
    linea_id = insertar_linea_salida(salida1, alimento_id, 49, caducidad='31-12-1999', lote='blabla', peso_unidad=1.0, valor_antiguo_uds=0)
    stock = stock_alimento(alimento_id, db)
    assert stock['stock'] == 51.0
    borrar_linea(linea_id=linea_id, es_entrada=False)
    stock = stock_alimento(alimento_id, db)
    assert stock['stock'] == 100.0
