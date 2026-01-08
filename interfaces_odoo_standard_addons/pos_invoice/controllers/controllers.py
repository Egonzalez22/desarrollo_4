# -*- coding: utf-8 -*-
# from odoo import http


# class PosInvoice(http.Controller):
#     @http.route('/pos_invoice/pos_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_invoice/pos_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_invoice.listing', {
#             'root': '/pos_invoice/pos_invoice',
#             'objects': http.request.env['pos_invoice.pos_invoice'].search([]),
#         })

#     @http.route('/pos_invoice/pos_invoice/objects/<model("pos_invoice.pos_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_invoice.object', {
#             'object': obj
#         })
