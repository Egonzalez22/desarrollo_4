# -*- coding: utf-8 -*-
{
    'name': "facturas_exportacion_fe",

    'summary': """
    Integración de las facturas de exportación con el módulo de facturación electrónica de Interfaces S.A.
    """,

    'description': """
        Integración de las facturas de exportación con el módulo de facturación electrónica de Interfaces S.A.

        Tarea N°152.299 - Se procedio a agregar el campo de narration en el footer del kude segun solicitud de la 
                        tarea.
    """,

    'author': "Interfaces S.A., Gustavo Bazan",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '2024.09.09.01',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sifen', 'facturacion_electronica_py', 'facturas_exportacion'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/kude_factura_exportacion.xml',
    ]
}
