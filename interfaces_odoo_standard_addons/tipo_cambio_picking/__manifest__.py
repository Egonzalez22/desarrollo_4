# -*- coding: utf-8 -*-
{
    'name': "Tipo de cambio en recepciones de Stock",

    'summary': """
        Tipo de cambio en recepciones de Stock        
""",

    'description': """
        Permite asignar el tipo de cambio con el cual serán calculados los costos de productos 
        que provengan de una Orden de compras en moneda extranjera 
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '20250326.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/stock_picking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
