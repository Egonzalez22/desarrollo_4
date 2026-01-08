# -*- coding: utf-8 -*-
{
    'name': "Aranceles en costos en destino",

    'summary': """
        Aranceles en costos en destino
        """,

    'description': """
        Agrega producto como Derecho Aduanero.
        Agrega aranceles en prorateo de costos en destino
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '2024.08.27.2',

    # any module necessary for this one to work correctly
    'depends': ['base','stock_landed_costs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/product.xml',
        'views/stock_landed_cost.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
