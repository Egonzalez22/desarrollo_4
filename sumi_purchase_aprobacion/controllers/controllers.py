# -*- coding: utf-8 -*-
# from odoo import http


# class SumiPurchaseAprobacion(http.Controller):
#     @http.route('/sumi_purchase_aprobacion/sumi_purchase_aprobacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sumi_purchase_aprobacion/sumi_purchase_aprobacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sumi_purchase_aprobacion.listing', {
#             'root': '/sumi_purchase_aprobacion/sumi_purchase_aprobacion',
#             'objects': http.request.env['sumi_purchase_aprobacion.sumi_purchase_aprobacion'].search([]),
#         })

#     @http.route('/sumi_purchase_aprobacion/sumi_purchase_aprobacion/objects/<model("sumi_purchase_aprobacion.sumi_purchase_aprobacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sumi_purchase_aprobacion.object', {
#             'object': obj
#         })
