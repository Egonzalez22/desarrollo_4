# -*- coding: utf-8 -*-
{
    'name': "rrhh_payroll_bancos_interfisa",

    'summary': """
        rrhh_payroll_bancos_interfisa
    
    """,

    'description': """
        Tarea N°26014 - se crea modulo para generacion de txt para banco interfisa
    """,

    'author': "Interfaces S.A., Edgar Gonzalez",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20240710.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'rrhh_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/res_company.xml',
        'reports/hr_payslip_run_banco_interfisa_report.xml',
        'reports/wizard_bancos_interfisa_report.xml'


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
