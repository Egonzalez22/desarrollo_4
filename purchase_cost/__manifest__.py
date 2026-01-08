# -*- coding: utf-8 -*-
{
    'name': "Costo de Venta en Compras",

    'summary': """
        Se agrega validación para evitar asiento de Costo en Compras""",

    'description': """
        Se agrega validación para evitar asiento de Costo en Compras
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '20241123.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','cotizacion_asientos_moneda_secundaria'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
