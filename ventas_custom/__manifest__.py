# -*- coding: utf-8 -*-
{
    'name': "ventas_custom",

    'summary': """
        Campos personalizados para el proceso de Analitica
    """,

    'description': """
        1 - Se agregan tablas menores para asociar a las lineas de presupuestos de ventas (metodologia, matriz, grupo)
        2 - En el menú configuración de sale.order se agrega el menú de ABM para las tablas menores
        3 - Se agrega un campo en compañia para definir si esta personalización se utiliza o no para dicha compañia
        4 - Ajustes varios a detallar, está relacionado al proceso de presupuestos para análitica (farma, alta complejidad y toxicologia)
        Tarea N°31739 - Se agregan nuevos campos al modelo de Grupo segun indicaciones en la tarea.
    """,

    'author': "Interfaces S.A., Gustavo Bazan",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '20250722.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'product', 'informes_presupuestos', 'sustancias_activas', 'stock', 'maintenance', 'quality_control'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/groups.xml',
        'data/company.xml',
        'data/data.xml',
        'views/res_company.xml',
        'views/ventas_metodologia.xml',
        'views/ventas_matriz.xml',
        'views/ventas_grupo.xml',
        'views/ventas_motivo.xml',
        'views/ventas_presentacion.xml',
        'views/ventas_volumen.xml',
        'views/ventas_metodologia_analisis.xml',
        'views/sale_order.xml',
        'views/product_template.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
        'report/presupuesto_farma.xml',
        'report/presupuesto_toxicologico.xml',
        'report/presupuesto_agroquimico.xml',
        'report/presupuesto_alta_complejidad.xml',
        'report/reporte_muestra.xml',
        'report/informe_de_control.xml',
        'wizards/informe_de_control.xml',
    ],
}
