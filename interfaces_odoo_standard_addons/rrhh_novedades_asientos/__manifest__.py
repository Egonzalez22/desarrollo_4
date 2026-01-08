# -*- coding: utf-8 -*-
{
    'name': "RRHH Novedades Asientos",

    'summary': """
        
        Si el campo "Usar cuentas de pagos pendientes" esta con el check entonces toma las cuentas de pago pendientes de la linea "Manual" del diario y si no esta cargado entonces 
        toma el campo "Cuenta de pagos pendientes" de contabilidad.
        
        """,

    'description': """
        Tarea N° 39.698 - Corrección en la generación de asientos de desembolsos de novedades

    """,

    'author': "Interfaces",
    'website': "https://www.interfaces.com.py",

    'category': 'Uncategorized',
    'version': '20241010.01',

    'depends': ['base','rrhh_novedades'],

    'data': [
        'views/hr_novedades_tipo.xml',

    ],

}
