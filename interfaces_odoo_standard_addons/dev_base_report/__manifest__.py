# -*- coding: utf-8 -*-
{
    'name': "dev_base_report",
    'summary': """Plantillas de reportes comunes de Odoo""",
    'description': """Plantillas de reportes comunes de Odoo""",

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20240912.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report_xlsx'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'reports/dev_base_report_wizard_views.xml',
        'reports/dev_base_report_wizard_templates.xml',
    ],
}
