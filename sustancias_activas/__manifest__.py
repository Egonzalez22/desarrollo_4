# -*- coding: utf-8 -*-
{
    'name': "sustancias_activas",

    'summary': """
    Agregar Campo de Sustancias Activas relacionado con los productos(metódos)    
    """,

    'description': """
        WIP Agregar Campo de Sustancias Activas relacionado con los productos(metódos)
        Tarea N°32.036 - Se procedio a modificar la vista desde producto para la carga de sustancias

    """,

    'author': "Intefaces S.A., Gustavo Bazan",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2024.05.30.01',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/company.xml',
        'views/product_template.xml',
        'views/sustancias_activas.xml',
    ],
}
