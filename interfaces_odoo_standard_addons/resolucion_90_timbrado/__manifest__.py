# -*- coding: utf-8 -*-
{
    'name': "resolucion_90_timbrado",

    'summary': """
        Agrega control de timbrado para autofactura
    """,

    'description': """
        Agrega control de timbrado para autofactura
    """,

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '2024.05.10.01',

    # any module necessary for this one to work correctly
    'depends': ['base', 'resolucion_90'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/account_journal.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
