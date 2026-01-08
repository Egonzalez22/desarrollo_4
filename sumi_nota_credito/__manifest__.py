# -*- coding: utf-8 -*-
{
    'name': "Sumi Nota de Crédito",

    'summary': """
        Restricción en Nota de Crédito.
    """,

    'description': """
        Tarea N°151.575 - SUMI: Restriccion de fecha de nota de credito emitida
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    'category': 'Uncategorized',
    'version': '20241031.01',

    'depends': ['base','account'],

    'data': [
        'views/account_move_reversal.xml',
        'security/data.xml',
    ],
}
