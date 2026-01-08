# -*- coding: utf-8 -*-
{
    'name': "Aprobación de Compras",

    'summary': """
        Aprobación de Compras""",

    'description': """
        Aprobación de Compras
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '20241210.1',

    # any module necessary for this one to work correctly
    'depends': ['base','nuevos_estados_presupuesto_compra'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/res_company.xml',
        'views/stock_picking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
