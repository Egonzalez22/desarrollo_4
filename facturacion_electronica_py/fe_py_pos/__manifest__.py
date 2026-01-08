# -*- coding: utf-8 -*-
{
    'name': "Facturación Electrónica POS",

    'summary': """
        Punto de Venta para Facturación Electrónica PY
    """,

    'description': """
        Punto de Venta para Facturación Electrónica PY
    """,

    'author': "Interfaces",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20241204.01',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'facturacion_electronica_py'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/factura_pos.xml',
        'views/pos_config.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'fe_py_pos/static/src/js/models.js',
            'fe_py_pos/static/src/js/PartnerDetailsEdit.js',
            'fe_py_pos/static/src/js/PartnerListScreen.js',
            'fe_py_pos/static/src/js/PaymentScreen.js',
            'fe_py_pos/static/src/js/InvoiceButton.js',
            'fe_py_pos/static/src/xml/PartnerDetailsEdit.xml',
            'fe_py_pos/static/src/xml/PartnerListScreen.xml',
            'fe_py_pos/static/src/css/pos_fe.css',
        ],
    },
}
