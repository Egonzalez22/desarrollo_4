# -*- coding: utf-8 -*-
{
    'name': "orden_pago",

    'summary': """
        Orden de pago
    """,

    'description': """
        Tarea N° 23.202 - se pasa modulo de orden de pago de terranova a sumi  
        23775: Númeración correlativa solamente al confirmar una orden de pago. No debe ser editable
        23776: Quitar wizard de referencia, agregar menú de impresión dentro de la orden de pago
    """,

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20250725.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/orden_pago.xml',
        'data/grupos.xml',
        'data/data.xml',
        # 'wizard/wizard_orden_pago.xml',
        'report/impresion_orden_pago_grupal.xml',
    ],
}
