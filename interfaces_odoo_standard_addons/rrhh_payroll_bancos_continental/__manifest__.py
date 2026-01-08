# -*- coding: utf-8 -*-
{
    'name': "Generar archivo para pago de salarios CONTINENTAL",

    'summary': """
Generar archivo TXT para pago de salarios CONTINENTAL desde el Lote de Salarios
""",

    'description': """
Generar archivo TXT para pago de salarios CONTINENTAL desde el Lote de Salarios
""",

    'author': "Interfaces S.A., Cristhian Cáceres",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '2024.1.24.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'rrhh_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/hr_employee.xml',
        'reports/hr_payslip_run_banco_continental_report.xml',
        'reports/wizard_bancos_continental_report.xml',
    ],
}
