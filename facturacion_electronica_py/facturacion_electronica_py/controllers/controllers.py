# -*- coding: utf-8 -*-
# from odoo import http


# class FacturacionElectronicaPy(http.Controller):
#     @http.route('/facturacion_electronica_py/facturacion_electronica_py', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/facturacion_electronica_py/facturacion_electronica_py/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('facturacion_electronica_py.listing', {
#             'root': '/facturacion_electronica_py/facturacion_electronica_py',
#             'objects': http.request.env['facturacion_electronica_py.facturacion_electronica_py'].search([]),
#         })

#     @http.route('/facturacion_electronica_py/facturacion_electronica_py/objects/<model("facturacion_electronica_py.facturacion_electronica_py"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('facturacion_electronica_py.object', {
#             'object': obj
#         })
