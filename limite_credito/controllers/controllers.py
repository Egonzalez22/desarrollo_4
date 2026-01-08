# -*- coding: utf-8 -*-
# from odoo import http


# class Facturas(http.Controller):
#     @http.route('/facturas/facturas', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/facturas/facturas/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('facturas.listing', {
#             'root': '/facturas/facturas',
#             'objects': http.request.env['facturas.facturas'].search([]),
#         })

#     @http.route('/facturas/facturas/objects/<model("facturas.facturas"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('facturas.object', {
#             'object': obj
#         })
