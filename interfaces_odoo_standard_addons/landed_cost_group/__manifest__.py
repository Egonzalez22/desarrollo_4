# -*- coding: utf-8 -*-
{
    'name': "Agrupar costos en destino",

    'summary': """
        Crear una sola operación de Costos en destino desde varias facturas""",

    'description': """
        Crear una sola operación de Costos en destino desde varias facturas
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','tipo_cambio_landed_costs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/stock_landed_cost.xml',
        'views/account_move.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
