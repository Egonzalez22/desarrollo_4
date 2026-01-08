# -*- coding: utf-8 -*-
{
    "name": "l10n_py_retenciones_grupo_account_payment",
    "summary": "Grupo de Pagos en Retenciones",
    "description": "Grupo de Pagos en Retenciones",
    "author": "Interfaces S.A., Cristhian Cáceres",
    "website": "https://www.interfaces.com.py",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Accounting",
    "version": "20250516.1",
    "license": "LGPL-3",
    # any module necessary for this one to work correctly
    "depends": ["base", "l10n_py_retenciones", "grupo_account_payment"],
    # always loaded
    "data": [
        "views/payment_group.xml",
    ],
}
