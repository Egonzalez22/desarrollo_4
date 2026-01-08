# -*- coding: utf-8 -*-
{
    'name': "Impresion de Cheques",

    'summary': """
         Formato de impresion de Cheques PY""",

    'description': """
        Impresion de cheques, con permisos para imprimir y contador de impresiones.
        Tarea N° 23.197 - se sube impresion de cheques de tipo a la vista y diferido.
        Cambios en Cheque guaranies
        Tarea N°23.517 - talon de cheque para dolares
        Tarea N°23.516 - Creacion de vista para cheque en dolares y se desarrolla su contenido
        Tarea N°23.518 - se reduce tamaño de hoja para lograr bajar la descripcion de numeros a letras
        Tarea N°23.521 - desarrollo de impresion directa, nota: como la impresion lo hace linea por linea, no se
                        se puede hacer mas para que la fecha suba o baje mas, ya que la forma en como lo hace no 
                        da mas formas de lograrlo. en cuanto a los demas puntos si salen donde deben, fuente ulizada 
                        debe de ser monoespaciada.
        Tarea N°23.520 - se desarrolla funcion que busque el numero de cuenta del banco seleccionado segun indicacion de la tarea
                       - Modificacion de funcion,  se crea campo de nro_cuenta_id para que sea un campo referenciado del modelo de res.partner.bank
                       a modo de que cuando seleccionen el banco se filtren las cuentas que tiene dicho banco.
                       
        Tarea N°26.020 - se agrega mas espacio para la impresion de numero a texto en cheque
    """,

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '2024.04.30.01', 

    # any module necessary for this one to work correctly
    'depends': ['base','account','interfaces_payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/account_payment.xml',
        'views/template_cheque.xml',
        'views/cheque_dolares.xml',
        # 'views/cheque_vision_vista.xml',
        # 'views/cheque_diferido.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
