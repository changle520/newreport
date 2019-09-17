#coding:utf8
from collections import namedtuple


Units = namedtuple('Units', ['weight', 'volume', 'global_unit', 'mole'])
units = Units(u'g', u'ml', u'u', u'mol')

# 单位的数据结构，{'g':{'g':0}}，0表示10的0次方
system_units = {
    units.weight: {u'kg': 3, u'千克': 3, u'公斤': 3,
                   u'g': 0, u'克': 0, u'mg': -3, u'毫克': -3,
                   u'mcg': -6, u'μg': -6, u'ug': -6, u'微克': -6},

    units.volume: {u'l': 3, u'升': 3, u'ml': 0, u'毫升': 0,
                   u'ul': -3, u'μl': -3, u'微升': -3},


    units.global_unit: {
        u'百万iu': 7, u'百万iμ': 7, u'百万单位': 7, u'百万u': 7, u'百万μ': 7,
        u'miu': 7, u'miμ': 7, u'm单位': 7, u'mu': 7, u'nμ': 7,
        u'万iu': 4, u'万iμ': 4, u'万单位': 4, u'万u': 4, u'万μ': 4,
        u'kiu': 3, u'kiμ': 3, u'k单位': 3, u'ku': 3, u'kμ': 3, u'千iu': 3, u'千iμ': 3, u'千单位': 3,
        u'千u': 3, u'千μ': 3, u'tiu': 3, u'tiμ': 3, u't单位': 3, u'tu': 3, u'tμ': 3,
        u'iu': 0, u'iμ': 0, u'单位': 0, u'u': 0, u'μ': 0},

    units.mole: {u'mol': 0, u'摩尔': 0, u'mmol': -3, u'毫摩尔': -3,
                 u'umol': -6, u'μmol': -6, u'微摩尔': -6}}


def get_system_unit(unit):
    # 获取单位的基准单位

    for base_unit, unit_map in system_units.items():

        if unit in unit_map:
            return base_unit
    return unit


def is_convert_able(a_unit, b_unit):
    # 两个单位能否相互转换

    return get_system_unit(a_unit) == get_system_unit(b_unit) if a_unit else False


def get_factor(source_unit, target_unit):
    # 获取单位转换系数，如'g'➡'kg',0-3=-3
    for base_unit, unit_map in system_units.items():
        if source_unit in unit_map:
            return unit_map.get(source_unit) - unit_map.get(target_unit)


def convert_dddUnit(value, unit, ddd_unit):
    # 获取单位转换后的值

    if is_convert_able(unit, ddd_unit):
        value *= 10**get_factor(unit, ddd_unit)
    else:
        value = 0.0
    return value, unit