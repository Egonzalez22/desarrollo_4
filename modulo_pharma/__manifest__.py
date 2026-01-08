# -*- coding: utf-8 -*-
{
    'name': "modulo_pharma",

    'summary': """
                modulo_pharma
    """,

    'description': """
       tarea N°24.359 - se crea abm para carga de resultado pharma segun indicaciones de la tarea
        Tarea N°24.372 - Se crea reporte de certificado pharma
                       - Se realizan cambios en el reporte.
        Tarea N°25.863 - Se realizan cambios solicitados segun la tarea
                       - Se modifica funcion que agrega lineas segun indicacion de la tarea.
        Tarea N°26.066 - Se realizaron cambios en la funcionalidad del formulatio y tambien se volvio a agregar el modelo de 
        detalle_pharma_line el cual ya se habia agregado al inicio pero que por se habia solicitado sacar y unificar con el modelo de
        resultados.pharma.sale, tambien se agregaron nuevos campos y se trabajo en el reporte de la certificacion.
                    - Se realizan correcciones en el reporte segun notas agregadas en la tarea. 
        Tarea N°26.066 - Se realizan cambios en el reporte, se desarrollo el formato indicado en la tarea lo mas parecido posible.
        Tarea N°26.342 - se agrega cambio al reporte segun indicacion de la tarea
                       - se realizan ajustes solicitados segun la descripcion de la tarea
                       - Modificaciones en reporte
        Tarea N°26.317 - Se procedio a crear campos nuevos y modificar funcionalidad de la carga de resultado, creacion de filtro y campos ocultos el cual se 
        utiliza dentro del reporte
                       - Se procede a agregar una validacion mas a la funcion de lotes, a modo de que excluya el lote que ya se registro en el modelo
                       y solo muestre el que no ha sido agregado aun.
        Tarea N°32.219 - modificacion en la funcionalidad de la carga de resultados y se crea nuevo campo
                       - se realizan modificaciones en funciones, se cambia numero de certificado
                       - se crea campo donde se guarda el codigo de muestra
    """,

    'author': "Interfaces S.A. - Edgar Gonzalez",
    'website': "http://www.interfaces.com.py",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '20241230.02',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product','mrp','sale', 'stock', 'hr', 'ventas_custom', 'l10n_py_set_cities'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/resultadopharma.xml',
        'report/reporte_pharma.xml',
        'views/product_template.xml',
        'views/certificados_laboratorio_views.xml',
        'views/mrp_workorder.xml',
        'views/resultados.xml',
        'report/reporte_certificado_laboratorio.xml',
        'report/reporte_certificado_alta_complejidad.xml',
        'report/reporte_certificado_agroquimico.xml',
        'report/reporte_certificado_toxicologico.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'modulo_pharma/static/src/js/tablet.js',
            'modulo_pharma/static/src/xml/tablet.xml',
        ],
    },
}
