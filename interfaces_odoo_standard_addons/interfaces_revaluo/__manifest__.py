# -*- coding: utf-8 -*-
{
    'name': "interfaces_revaluo",

    'summary': """
        Módulo para reporte de cuadro de depreciación
        """,

    'description': """
        Módulo para reporte de cuadro de depreciación y revaluo de activos fijos
    """,

    'author': "Interfaces S.A., Gustavo Bazan",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '20250225.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_asset'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_asset.xml'
    ],
}
