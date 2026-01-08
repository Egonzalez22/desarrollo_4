# -*- coding: utf-8 -*-
{
    'name': "Facturación Electrónica Personalizacion",

    'summary': """
        Personalización de facturación electrónica para Sumi
    """,

    'description': """
        1. 23840: Se agrega nro de presupuesto en el kude
    """,

    'author': "Interfaces S.A., Gustavo Bazan",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20250428.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sifen', 'facturacion_electronica_py'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/kude_factura.xml',
    ],
}
