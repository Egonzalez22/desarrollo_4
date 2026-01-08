# -*- coding: utf-8 -*-
# from odoo import http


# class ClonarPricelist(http.Controller):
#     @http.route('/clonar_pricelist/clonar_pricelist', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/clonar_pricelist/clonar_pricelist/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('clonar_pricelist.listing', {
#             'root': '/clonar_pricelist/clonar_pricelist',
#             'objects': http.request.env['clonar_pricelist.clonar_pricelist'].search([]),
#         })

#     @http.route('/clonar_pricelist/clonar_pricelist/objects/<model("clonar_pricelist.clonar_pricelist"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('clonar_pricelist.object', {
#             'object': obj
#         })
