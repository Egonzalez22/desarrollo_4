# -*- coding: utf-8 -*-
{
    'name': "Cajas",

    'summary': """
       Agrega funcionalidad de cajas de pagos""",

    'description': """
        Agrega funcionalidad de cajas de pagos
        Tarea GC N° 39.741 -  se agrego validacion de excluir diario de la validacion de
                               sesion de caja
        Tarea GC N°31.733 -  Se agrega a la sesion de caja las salidas de dinero, segun pedido del cliente
        Tarea GC N°151.700 - Se realiza cambios segun indicaciones de la tarea.
        Tarea N°152730: Error de sesión de caja - Ajuste en función de verifación de sesión de caja
    """,

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '20241122.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/cajas.xml',
        'views/caja_session.xml',
        'views/reporte_sesion_caja.xml',
        'views/account_journal.xml',
    ],
}
