# -*- coding: utf-8 -*-
{
    'name': "Límite de Crédito",

    'summary': """
        Límite de Crédito para clientes
    """,

    'description': """
        1 - WIP
        Tarea N° 24.870 -  Se agrega validacion dentro de la accion de servidor que valida varias facturas a la vez desde el listado de 
                           facturas
    """,

    'author': "Interfaces",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20240902.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'contacts'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/groups.xml',
        'views/res_partner.xml',
        'views/account_payment.xml',
        'report/solicitud_credito.xml'
    ],
}
