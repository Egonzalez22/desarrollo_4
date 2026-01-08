# -*- coding: utf-8 -*-
{
    'name': "reportes_ventas_cobranzas",

    'summary': """
        Reporte de Ventas y Cobranzas
    """,

    'description': """
        Reporte de Ventas y Cobranzas.
        Tarea N° 20.201 - Se subsanan error en reporte de ventas cobranzas en la opcion de "Repore Cobranzas"
        y se comenta opcion de ventas_acumuladas segun inidicaciones de la tarea.

        Se agrega validacion para que solo muestre cabeceras dentro del reporte si es que tiene datos nada mas.
        Tarea N°21747 
                    - se verifica y se mejora informe segun indicaciones de la tarea
                    - Se cambia a formato solicitado por el cliente segun indicacion de la tarea
        Tarea N° 22.374 -  Ajuste para la columna de retencion en el reporte de cobranzas ventas, segun 
        indicaciones de la tarea
        Tarea N° 22.772 - se realizan ajustes en calculo para formas de pagos segun lo indicado en la tarea
        Cliente Sumi
        Tarea N°28137 - se modifica posicion de columnas segun indicacion en nota de la tarea
                    - modificaciones en reporte
        Tarea N°39723 - Se realizan varias modificaciones dentro del reporte por el error que daba.
    """,

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '20241028.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
