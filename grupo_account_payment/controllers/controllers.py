# -*- coding: utf-8 -*-
from odoo import http

# class GrupoAccountPayment(http.Controller):
#     @http.route('/grupo_account_payment/grupo_account_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/grupo_account_payment/grupo_account_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('grupo_account_payment.listing', {
#             'root': '/grupo_account_payment/grupo_account_payment',
#             'objects': http.request.env['grupo_account_payment.grupo_account_payment'].search([]),
#         })

#     @http.route('/grupo_account_payment/grupo_account_payment/objects/<model("grupo_account_payment.grupo_account_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('grupo_account_payment.object', {
#             'object': obj
#         })