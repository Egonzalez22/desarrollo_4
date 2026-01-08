# -*- coding: utf-8 -*-
{
    'name': "Factura Multi Pago",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2024.02.16.03',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'interfaces_payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/multi_pago.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'factura_multi_pago/static/src/js/factura_multi_pago.js',
        ],
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
