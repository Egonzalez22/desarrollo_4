# -*- coding: utf-8 -*-
{
    'name': "account_cajas_sumi",

    'summary': """
        Módulo para personalizar el módulo de cajas para sumi
    """,

    'description': """
        32142: Error en sesión de cajas al restablecer pagos a borrador se duplica el registro
    """,

    'author': "Interfaces S.A., Gustavo Bazan",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '20241210.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_cajas', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',,
    ],
}
