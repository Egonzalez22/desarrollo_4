# -*- coding: utf-8 -*-
# from odoo import http


# class FacturasExportacion(http.Controller):
#     @http.route('/facturas_exportacion/facturas_exportacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/facturas_exportacion/facturas_exportacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('facturas_exportacion.listing', {
#             'root': '/facturas_exportacion/facturas_exportacion',
#             'objects': http.request.env['facturas_exportacion.facturas_exportacion'].search([]),
#         })

#     @http.route('/facturas_exportacion/facturas_exportacion/objects/<model("facturas_exportacion.facturas_exportacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('facturas_exportacion.object', {
#             'object': obj
#         })
