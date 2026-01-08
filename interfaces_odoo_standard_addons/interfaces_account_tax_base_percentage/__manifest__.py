# -*- coding: utf-8 -*-
{
    'name': "Impuesto aplicado sobre sobre un porcentaje de la base",
    'summary': "Impuesto aplicado sobre sobre un porcentaje de la base (Solo para reportes)",
    'description': "Impuesto aplicado sobre sobre un porcentaje de la base (Solo para reportes)",

    'author': "Interfaces S.A., Cristhian Cáceres",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '20250603.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'views/account_tax.xml',
    ],
}
