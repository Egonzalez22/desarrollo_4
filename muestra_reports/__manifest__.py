# -*- coding: utf-8 -*-
{
    'name': "muestra_reports",

    'summary': """
       muestra_reports
       
    """,

    'description': """
       muestra_reports
       Tarea N° 32.429 - se procedio a crear un reporte donde se muestra los analisis solicitados.
                       - se agregan mas datos segun nota agregada a la tarea 

    """,

    'author': "Interfaces S.A. - Edgar Gonzalez",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2024.10.16.01',

    # any module necessary for this one to work correctly
    'depends': ['base', 'ventas_custom'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/ingreso_muestra.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
