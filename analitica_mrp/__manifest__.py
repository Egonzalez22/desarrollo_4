# -*- coding: utf-8 -*-
{
    'name': "Ajustes en Fabricación para Analitica SA",
    'summary': """
        Ajustes en Fabricación para Analitica SA""",
    'description': """
        Ajustes en Fabricación para Analitica SA
    """,
    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",
    'category': 'MRP',
    'version': '20250718.1',
    'depends': ['base','ventas_custom','mrp'],
    'data': [
        'views/mrp_production.xml',
        'views/mrp_workorder.xml',
    ],
}
