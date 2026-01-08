# -*- coding: utf-8 -*-
{
    'name': "URLs explícitas para Links Trackeados",

    'summary': """
Habilita la definición explícita de las URLs base para los links trackeados 
        """,

    'description': """
Habilita la definición explícita de las URLs base para los links trackeados 
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Marketing',
    'version': '20241223.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'social', 'mass_mailing'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_company.xml',
        'views/link_tracker.xml',
        'views/social_post.xml',
        'views/mailing_mailing.xml',
    ],
}
