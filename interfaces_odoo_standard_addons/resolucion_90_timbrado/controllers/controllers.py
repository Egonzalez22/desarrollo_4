# -*- coding: utf-8 -*-
# from odoo import http


# class Resolucion90Timbrado(http.Controller):
#     @http.route('/resolucion_90_timbrado/resolucion_90_timbrado', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/resolucion_90_timbrado/resolucion_90_timbrado/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('resolucion_90_timbrado.listing', {
#             'root': '/resolucion_90_timbrado/resolucion_90_timbrado',
#             'objects': http.request.env['resolucion_90_timbrado.resolucion_90_timbrado'].search([]),
#         })

#     @http.route('/resolucion_90_timbrado/resolucion_90_timbrado/objects/<model("resolucion_90_timbrado.resolucion_90_timbrado"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('resolucion_90_timbrado.object', {
#             'object': obj
#         })
