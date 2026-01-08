# -*- coding: utf-8 -*-
{
    'name': "sifen",

    'summary': """
        Módulo para interactuar con SIFEN
    """,

    'description': """
        Módulo para interactuar con SIFEN
    """,

    'author': "Interfaces",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '20250306.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'interfaces_timbrado', 'notas_remision_account', 'standard_ruc', 'interfaces_tools'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/groups.xml',
        'data/cron.xml',
        'data/company.xml',
        'views/account_move.xml',
        'views/lote.xml',
        'views/anular_facturas_wizard.xml',
        'views/inutilizar_facturas_registros.xml',
        'views/nota_remision.xml',
        'views/res_partner.xml',
        'views/product_template.xml'
    ],
}
