# -*- coding: utf-8 -*-
{
    'name': "reparacion_personalizacion",

    'summary': """
        reparacion_personalizacion
        
        """,

    'description': """
          tareas realizadas:
          22.836 - Se agrega dentro de la vista de pago el id como numero de recibo interno
          22.778 - se crea campo nuevo de codigo de cliente dentro de ordenes de cliente
          20.238 - se agrega campo nuevo dentro de presupuestos
          20.206 - se agrega campos nuevos para lo que seria el punto de control del modulo de calidad 
          visible solo para la compañia Analitica SA
          22.871 - Se procede a agregar el id del pago registrado en el recibo como forma de numero de recibo interno
          23.198 - Se agrega linea de retenciones para que muestre en el caso de que tenga la orden de pago
          23.865 - se cambia numero de recbo 
          23.591 - se comenta cambio que se habia hecho alguna vez en recibo de pago
          25.819 -  se agrega al campo nro_recibo el datos que se genera en el campo de name
                 -  se revierte forma en que se agrega el numero de recibo para pagos de clientes y se crea secuencia con el odoo
                 -  se crea campo nuevo donde se guardara el numero de recibo original creado por la secuencia
    """,

    'author': "Interfaces - Edgar Gonzalez",
    'website': "https://www.interfaces.com.py",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20240903.01',

    # any module necessary for this one to work correctly
    'depends': ['base','sale', 'helpdesk_repair', 'mrp_workorder', 'account', 'interfaces_payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/repair_order.xml',
        'views/quality_point_form.xml',
        'views/account_payment.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
