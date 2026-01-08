# -*- coding: utf-8 -*-
{
    'name': "interfaces_tipo_cambio_compra_venta_v16",

    'summary': """
        Tipos de cambio de Compra y Venta en las monedas. Cambios exclusivos para las vistas de la versión 16
    """,

    'description': """
        Tipos de cambio de Compra y Venta en las monedas. Cambios exclusivos para las vistas de la versión 16
    """,

    'author': "Interfaces S.A., Cristhian Cáceres",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '20240829.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'interfaces_tipo_cambio_compra_venta'],

    # always loaded
    'data': [
        'views/account_bank_statement_line.xml',
        'views/bank_rec_widget.xml',
    ],
}
