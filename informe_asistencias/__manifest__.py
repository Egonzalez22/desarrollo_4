# -*- coding: utf-8 -*-
{
    'name': "informe_asistencias",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Se copia reporte del proyecto de impakta version 15
        tarea N°23.916 - se descomenta parta de funcion para prueba en test
    """,

    'author': "Interfaces S.A., Edgar Gonzalez",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2023.03.11.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report_xlsx', 'hr', 'hr_attendance'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/wizard.xml',
        'views/reporte_informe_asistencias.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
