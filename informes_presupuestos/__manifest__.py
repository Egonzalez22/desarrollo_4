# -*- coding: utf-8 -*-
{
    'name': "Presupuestos de Ventas",

    'summary': """
        Presupuestos de ventas personalizados para los equipos Analítico, Preventivo, Correctivo y Calificativo
    """,

    'description': """
        1 - Presupuesto para Equipos Analítico
        2 - Presupuesto para Equipos Correctivo
        3 - Presupuesto para Equipos Preventivo
        4 - Presupuesto para Equipos Calificativo
        5 - Se agrega codigo de fabricante en el producto
        6 - Se agregan campos personalizables para los presupuestos de ventas
        Tarea N°23.727 - se realiza cambio segun la indicacion de la tarea
        Tarea N°151.686 - SUMI: Layouts de cotizaciones para postventa
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py, Gustavo Bazan",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20241209.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'interfaces_tools', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/sale_order.xml',
        'views/product_template.xml',
        'report/1_informe_analitico.xml',
        # 'report/2_informe_preventivo.xml',
        'report/3_informe_correctivo.xml',
        'report/4_informe_calificativo.xml',
    ],
}
