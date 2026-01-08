# -*- coding: utf-8 -*-
{
    'name': "WhatsApp Cloud API",

    'summary': """
        Integración con WhatApp Cloud API   
    """,

    'description': """
        Integración con WhatApp Cloud API   

    """,

    'author': "Interfaces.com.py",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Communications',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/message.xml',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
