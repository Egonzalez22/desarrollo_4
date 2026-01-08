# -*- coding: utf-8 -*-
# from odoo import http


# class OrdenPago(http.Controller):
#     @http.route('/orden_pago/orden_pago', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/orden_pago/orden_pago/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('orden_pago.listing', {
#             'root': '/orden_pago/orden_pago',
#             'objects': http.request.env['orden_pago.orden_pago'].search([]),
#         })

#     @http.route('/orden_pago/orden_pago/objects/<model("orden_pago.orden_pago"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('orden_pago.object', {
#             'object': obj
#         })
