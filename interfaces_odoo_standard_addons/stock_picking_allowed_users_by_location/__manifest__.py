# -*- coding: utf-8 -*-
{
    'name': "stock_picking_allowed_users_by_location",

    'summary': """
Restricciones en la validación del picking según qué usuarios tiene permitido añadir o quitar existencias de un depósito
""",

    'description': """
Restricciones en la validación del picking según qué usuarios tiene permitido añadir o quitar existencias de un depósito
""",

    'author': "Interfaces S.A., Cristhian Cáceres",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '2024.4.16.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'views/stock_location.xml',
    ],
}
