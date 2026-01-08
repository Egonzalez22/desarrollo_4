# -*- coding: utf-8 -*-
{
    'name': "Facturas Interfaces",

    'summary': """
        Facturas Interfaces
        """,

    'description': """
        Facturas Interfaces
    """,

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Invoicing',

    'version': '2023.01.10.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'interfaces_tools'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/factura.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
