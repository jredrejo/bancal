#!/usr/bin/env python

'''py.test test cases to test people application.

These tests run simulating web2py shell environment and don't use webclient
module.

So, they run faster and don't need web2py server running.

If you want to see webclient approach, see test_people_controller_webclient.py
in this same directory.
'''
import pytest

def test_beneficiarios_fill(web2py):
    db=web2py.db
    rows=db(db.Beneficiario.id>0).select()
    assert len(rows)>0
