# -*- coding: utf-8 -*-
{
    'name': "bloqueo_contable",

    'summary': """
        bloqueo_contable
    """,

    'description': """
        RESTRINGIR LA CARGA DE FACTURAS, ASIENTOS CONTABLES, CON LA FECHA DE BLOQUEO (No permito que se carguen facturas, asientos contables
        con fecha menor o igual a la fecha de bloqueo contable)
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20260623.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
