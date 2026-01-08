# -*- coding: utf-8 -*-
{
    'name': "Standard RUC",

    'summary': """
        Cambia las traducciones de los formularios y reportes y les asigna el nombre RUC,
         en algunos casos los pone como requeridos""",

    'description': """
        Cambia las traducciones de los formularios y reportes y les asigna el nombre RUC,
         en algunos casos los pone como requeridos
    """,

    'author': "Interfaces S.A., Cristhian Cáceres",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localizaciones',
    'version': '2024.4.5.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'standard_ruc', 'account'],

    # always loaded
    'data': [
        'views/res_config_settings.xml',
    ],
}
