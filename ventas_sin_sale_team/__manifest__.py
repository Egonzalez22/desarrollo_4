# -*- coding: utf-8 -*-
{
    'name': "Acceso a ventas sin ser del Sale Team",

    'summary': """Permite el acceso a ventas a cualquier usuario con el permiso""",

    'description': """Permite el acceso a ventas a cualquier usuario con el permiso""",

    'author': "Interfaces",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2024.07.31',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        #'views/sale_order.xml',
        'group/group.xml',
        'security/ir.model.access.csv',
    ],
}
