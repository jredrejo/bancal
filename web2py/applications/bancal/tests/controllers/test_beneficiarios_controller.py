# -*- coding: utf-8 -*-


def test_beneficiarios_fill(web2py):
    db = web2py.db
    rows = db(db.Beneficiario.id > 0).select()
    assert len(rows) > 0
