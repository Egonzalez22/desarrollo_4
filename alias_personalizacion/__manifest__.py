# -*- coding: utf-8 -*-
{
    'name': "Personalizacion para cambio de Seudonimo",

    'summary': """
        Personalizacion para cambio de seudonimo al cambiar de empresa""",

    'description': """
        Personalizacion de alias para el dominio analitica
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",
    
    'category': 'Uncategorized',
    'version': '20250522.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','base_setup', 'bus', 'web_tour'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
