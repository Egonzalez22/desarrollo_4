# -*- coding: utf-8 -*-
{
    'name': "l10n_py_set_cities",
    'summary': "l10n_py_set_cities",
    'description': "l10n_py_set_cities",

    'author': "Interfaces S.A.",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '20240214.5',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'base_address_extended'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/res.country.state.csv',
        'data/res.district.csv',
        'data/res.city.csv',
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/res_country.xml',
        'views/res_district.xml',
        'views/res_city.xml',
    ],
}
