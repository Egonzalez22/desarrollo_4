# -*- coding: utf-8 -*-
{
    'name': "orden_personalizacion",

    'summary': """
        orden_personalizacion
    """,

    'description': """
        

    """,

    'author': "Interfaces S.A. - Edgar Gonzalez",
    'website': "http://www.interfaces.com.py",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2024.01.30.01',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'interfaces_tools'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        # 'report/recibo_a5.xml',
        'report/orden_pago.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
