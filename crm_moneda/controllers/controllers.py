# -*- coding: utf-8 -*-
# from odoo import http


# class CrmMoneda(http.Controller):
#     @http.route('/crm_moneda/crm_moneda/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_moneda/crm_moneda/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_moneda.listing', {
#             'root': '/crm_moneda/crm_moneda',
#             'objects': http.request.env['crm_moneda.crm_moneda'].search([]),
#         })

#     @http.route('/crm_moneda/crm_moneda/objects/<model("crm_moneda.crm_moneda"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_moneda.object', {
#             'object': obj
#         })
