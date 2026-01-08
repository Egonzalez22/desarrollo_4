# -*- coding: utf-8 -*-
# from odoo import http


# class Ajustes(http.Controller):
#     @http.route('/ajustes/ajustes', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ajustes/ajustes/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ajustes.listing', {
#             'root': '/ajustes/ajustes',
#             'objects': http.request.env['ajustes.ajustes'].search([]),
#         })

#     @http.route('/ajustes/ajustes/objects/<model("ajustes.ajustes"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ajustes.object', {
#             'object': obj
#         })
