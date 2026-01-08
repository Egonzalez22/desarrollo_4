# -*- coding: utf-8 -*-
{
    'name': "sumi_formato_recibo_salario",

    'summary': """Modifica los recibos de salarios para que muestren el salario del contrato.""",

    'description': """Modifica los recibos de salarios para que muestren el salario del contrato""",

    'author': "Interfaces",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20241213.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'rrhh_payroll'],

    # always loaded
    'data': [
        'views/custom_nomina.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
