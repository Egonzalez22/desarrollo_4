# -*- coding: utf-8 -*-
{
    'name': "firmas_recibos",

    'summary': """
        firmas_recibos
    """,

    'description': """
        Tarea N°153.813 - Se procede a crear un campo en empleados, para que puedan ingresar su firma el cual sera llamado 
        en el reporte del recibo.

    """,

    'author': "Interfaces S.A., Edgar Gonzalez",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2024.11.11.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'interfaces_payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/hr_employee.xml',
        'views/recibo_dinero.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
