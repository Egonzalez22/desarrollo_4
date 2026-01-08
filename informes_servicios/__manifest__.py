# -*- coding: utf-8 -*-
{
    'name': "Informes Servicios",

    'summary': """
        Informes para Tickets de Servicios
    """,

    'description': """
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py, Gustavo Bazan",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20250606.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'helpdesk', 'industry_fsm', 'project', 'hr_timesheet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/data.xml',
        'views/helpdesk_ticket.xml',
        'views/project_task.xml',
        'report/solicitud_servicio.xml',
        'report/certificado_servicio.xml',
        'report/worksheet_custom_report.xml',
        'report/solicitud_servicio_calificacion_calibracion.xml',
        'report/reporte_servicio.xml',
    ],
}
