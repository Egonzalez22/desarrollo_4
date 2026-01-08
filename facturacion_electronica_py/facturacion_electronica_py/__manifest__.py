# -*- coding: utf-8 -*-
{
    'name': "Facturación Electrónica Paraguay",

    'summary': """
        Facturación Electrónica Paraguay""",

    'description': """
        Módulo base para implementación de Facturación electrónica en Paraguay
    """,

    'author': "Interfaces S.A., Edgar Páez",
    'website': "http://www.interfaces.com.py",
    'icon': '/base/static/img/country_flags/py.png',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '20250212.5',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'contacts', 'interfaces_timbrado', 'sifen', 'l10n_py_set_cities'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/uom_uom.xml',
        'views/account_journal.xml',
        'views/account_move.xml',
        'views/res_users.xml',
        'views/kude_factura.xml',
        'views/kude_autofactura.xml',
        'views/kude.xml',
        'views/kude_factura.xml',
        'views/kude_autofactura.xml',
        'views/timbrado.xml',
        'views/kude_remision.xml',
        'views/kude_ticket.xml',
        'views/kude_ticket_factura.xml',
        'views/actividad_economica.xml',
    ],
}
