# -*- coding: utf-8 -*-
{
    'name': "Formato de Asistencia XLS",

    'summary': """
        Ajuste en el formato de impresion en XLS""",

    'description': """
         Ajuste en el formato de impresion de asistencias en XLS de manera a que se muestre en el formato de hora la marcación de entrada,
         marcación de salida y horas laborales.
    """,

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '20241106.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'hr_attendance','rrhh_asistencias'],

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
