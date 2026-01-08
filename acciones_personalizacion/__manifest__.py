# -*- coding: utf-8 -*-
{
    'name': "acciones_personalizacion",

    'summary': """
       acciones_personalizacion
    """,

    'description': """
        Tarea N°23.119 - Accion planificada, para cobranza agil
        Tarea N°19.445 - Accion planificada para control de facturas no cobradas, bloqueando al cliente despues de 60 dias de atraso
                       - Se agrega nuevas condiciones en la funcion para que tenga en cuenta eso a la hora de ejecutarse
                       - Cambios segun indicaciones en comentario
    """,

    'author': "Interfaces S.A. - Edgar Gonzalez",
    'website': "https://www.interfaces.com.py",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20240701.10',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_journal.xml',
        'data/cron_control_asiento.xml',
        'views/account_payment_term.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
