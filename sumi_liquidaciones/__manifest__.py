# -*- coding: utf-8 -*-
{
    'name': "sumi_liquidaciones",

    'summary': """

        sumi_liquidaciones
        
    """,

    'description': """
        Tarea N°160.510 - se procede a apdaptar codigo realizado en el cliente cysa, se agrega campo de motivo de salida en 
        wizard de despido y renuncia, asi como un boton con una accion de agregar el motivo de salida en la vista de 
        contratos.
    """,

    "author": "Interfaces S.A., Edgar Gonzalez",
    "website": "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'RRHH',
    "version": "20250728.2",

    # any module necessary for this one to work correctly
    'depends': ['base', "rrhh_liquidacion", "hr_payroll", "hr_contract"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_calculo_despido.xml',
        'views/wizard_calculo_renuncia.xml',
        'views/hr_contract.xml',
        'views/wizard_cancelar_contrato.xml',

    ],

}
