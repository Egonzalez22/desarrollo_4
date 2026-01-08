# -*- coding: utf-8 -*-
{
    "name": "Gestión de retenciones",
    "summary": "Gestión de Retenciones - Paraguay",
    "description": """
Gestión de retenciones - Paraguay
    """,
    "author": "Interfaces S.A.",
    "website": "https://www.interfaces.com.py",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Account",
    "version": "20250602.1",
    "license": "LGPL-3",
    # any module necessary for this one to work correctly
    "depends": ["base", "account_accountant", "standard_ruc", "proveedores_timbrado"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/res_company.xml",
        "views/account_payment.xml",
        "views/res_config_settings.xml",
        "views/retencion_rule.xml",
        "views/res_partner.xml",
        "views/account_move.xml",
        "views/emitir_retencion_wizard.xml",
    ],
}
