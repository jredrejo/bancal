#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
from applications.searchprice.modules.util_www import *


def test_get_flag():
    assert "/ES.png" in get_flag('Spain')
    assert "/GB.png" in get_flag('United Kingdom')
    assert "/US.png" in get_flag('USA')
    assert "/US.png" in get_flag('United States')


def test_country_code():
    assert country_code('Spain') == 'esp'
    assert country_code('United Kingdom') == 'gbr'
    assert country_code('USA') == 'usa'
    assert country_code('United States') == 'usa'
    assert country_code('South-Africa') == 'zaf'
    assert country_code('Northern Ireland') == 'gbr'


def test_geoip():
    from applications.searchprice.models.aaa_const import SETTINGS
    SETTINGS['DEBUGGER'] = False
    assert geoip('188.78.107.127')[0] == 'esp'
    assert geoip('212.83.40.17')[0] == 'deu'


def test_fix_country_name():
    assert fix_country_name("United-States") == 'USA'
"""
