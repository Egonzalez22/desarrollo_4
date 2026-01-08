# -*- coding: utf-8 -*-
{
    'name': "etiqueta_analitica",

    'summary': """
        Se personaliza la impresión de etiquetas de analitica
    """,

    'description': """
        1 - WIP
        Tarea N°32.289 - Se procedio a modificar campo de donde debe de llamar el dato para codigo de muestra, segun 
                        la indicacion de la tarea.
        Tarea N°152.309 - ET/2024/0066 - ANALITICA: Nuevos ajustes en Etiqueta en Recepción de muestras
    """,

    'author': "Interfaces S.A., Gustavo Bazan",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20250512.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'ventas_custom'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking.xml',
        'report/etiqueta_analitica.xml',
    ],
}
