# -*- coding: utf-8 -*-
{
    'name': "Clonar lista de precios",

    'summary': """
        Permite clonar los items de una lista de precios a otra. 
        """,

    'description': """
        Permite clonar los items de una lista de precios a otra. 
        Esto se desarrolló como medida correctiva a un problema de Odoo donde no convierte precios de una lista de precios en USD a Gs.
        Solo se debe utilizar cuando se desea clonar items de tarifas con precio fijo.
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/wizard_clone_pricelist.xml',
        'views/pricelist.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
