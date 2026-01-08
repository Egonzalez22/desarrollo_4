# -*- coding: utf-8 -*-
{
    'name': "Nuevos Estados Presupuesto",

    'summary': """Nuevos Estados Presupuestos de Compra""",

    'description': """Se agregan nuevos estados al presupuesto de compra""",

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2024.07.19',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': ['views/purchase_views.xml'],
}
