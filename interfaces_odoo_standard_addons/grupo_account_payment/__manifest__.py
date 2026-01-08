# -*- coding: utf-8 -*-
{
    "name": "Grupos de pagos",
    "summary": """
        Grupos de pagos
        """,
    "description": """
        - Añade la funcionalidad de agrupar diferentes métodos de pago en un solo recibo u orden de pago.
        - Permite la asignación de pagos parciales.
    """,
    "author": "Interfaces S.A.",
    "website": "http://www.interfaces.com.py",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Account",
    "version": "20250612.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "account", "interfaces_payment"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/account_move.xml",
        "views/account_invoice.xml",
        "views/reporte_pagos.xml",
        "views/payment_group.xml",
        "views/account_payment.xml",
        "views/account_journal.xml",
    ],
    # only loaded in demonstration mode
    "post_init_hook": "post_init_hook",
}
