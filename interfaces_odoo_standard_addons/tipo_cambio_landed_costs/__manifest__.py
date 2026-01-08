# -*- coding: utf-8 -*-
{
    'name': "Tipo de cambio en Costos en destino",

    'summary': """
        Tipo de cambio en Costos en destino""",

    'description': """
        Cuando se crea un costo en destino desde una factura de proveedor, el sistema convierte el valor del costo en destino 
        según el tipo de cambio que se estableció para dicha factura. Asegurando que no haya inconsistencias en el costeo de productos 
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '2023.10.18.01',

    # any module necessary for this one to work correctly
    'depends': ['base','stock_landed_costs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
