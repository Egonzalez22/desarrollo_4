# -*- coding: utf-8 -*-
{
    'name': "facturas_exportacion",

    'summary': """
    Se habilitan campos para factura de exportación
    """,

    'description': """
        Se habilitan campos para factura de exportación
    """,

    'author': "Interfaces S.A., Gustavo Bazan",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '2023.12.27.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_journal.xml',
        'views/account_move.xml',
    ]
}
