# -*- coding: utf-8 -*-
# from odoo import http


# class IntegracionFe(http.Controller):
#     @http.route('/integracion_fe/integracion_fe', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/integracion_fe/integracion_fe/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('integracion_fe.listing', {
#             'root': '/integracion_fe/integracion_fe',
#             'objects': http.request.env['integracion_fe.integracion_fe'].search([]),
#         })

#     @http.route('/integracion_fe/integracion_fe/objects/<model("integracion_fe.integracion_fe"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('integracion_fe.object', {
#             'object': obj
#         })
