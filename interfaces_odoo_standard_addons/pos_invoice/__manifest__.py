# -*- coding: utf-8 -*-
{
    'name': "Factura Autoimpresor en POS",

    'summary': """
       Cambia el formato de la factura por defecto en el pos, por la factura autoimpresor""",

    'description': """
        Cambia el formato de la factura por defecto en el pos, por la factura autoimpresor
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'POS',
    'version': '2023.12.05.01',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','factura_autoimpresor'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_invoice/static/src/js/models.js',
            'pos_invoice/static/src/js/InvoiceButton.js',
        ]
    }
}
