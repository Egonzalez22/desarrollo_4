# -*- coding: utf-8 -*-
# from odoo import http


# class InterfacesImpresionCheque(http.Controller):
#     @http.route('/interfaces_impresion_cheque/interfaces_impresion_cheque/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/interfaces_impresion_cheque/interfaces_impresion_cheque/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('interfaces_impresion_cheque.listing', {
#             'root': '/interfaces_impresion_cheque/interfaces_impresion_cheque',
#             'objects': http.request.env['interfaces_impresion_cheque.interfaces_impresion_cheque'].search([]),
#         })

#     @http.route('/interfaces_impresion_cheque/interfaces_impresion_cheque/objects/<model("interfaces_impresion_cheque.interfaces_impresion_cheque"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('interfaces_impresion_cheque.object', {
#             'object': obj
#         })
