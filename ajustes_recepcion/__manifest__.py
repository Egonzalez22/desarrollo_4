# -*- coding: utf-8 -*-
{
    'name': "Ajustes en Recepción",

    'summary': """
        Ajustes personalizados en la recepción de muestras""",

    'description': """
        ID 151.214 - Ticket
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '20240717.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','ventas_custom'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
