# -*- coding: utf-8 -*-
# from odoo import http


# class Sifen(http.Controller):
#     @http.route('/sifen/sifen', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sifen/sifen/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sifen.listing', {
#             'root': '/sifen/sifen',
#             'objects': http.request.env['sifen.sifen'].search([]),
#         })

#     @http.route('/sifen/sifen/objects/<model("sifen.sifen"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sifen.object', {
#             'object': obj
#         })
