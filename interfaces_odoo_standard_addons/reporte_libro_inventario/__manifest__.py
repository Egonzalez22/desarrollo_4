# -*- coding: utf-8 -*-
{
    'name': "Reporte Libro Inventario",

    'summary': """Reporte Libro Inventario""",

    'description': """Reporte Libro Inventario""",

    'author': "Interfaces S.A., Cristhian Cáceres",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2023.11.9.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'l10n_py_reports'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/reporte_libro_inventario.xml',
        'reports/wizard_reporte_libro_inventario.xml',
    ],
}
