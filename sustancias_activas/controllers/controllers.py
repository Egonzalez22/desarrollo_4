# -*- coding: utf-8 -*-
# from odoo import http


# class SustanciasActivas(http.Controller):
#     @http.route('/sustancias_activas/sustancias_activas', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sustancias_activas/sustancias_activas/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sustancias_activas.listing', {
#             'root': '/sustancias_activas/sustancias_activas',
#             'objects': http.request.env['sustancias_activas.sustancias_activas'].search([]),
#         })

#     @http.route('/sustancias_activas/sustancias_activas/objects/<model("sustancias_activas.sustancias_activas"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sustancias_activas.object', {
#             'object': obj
#         })
