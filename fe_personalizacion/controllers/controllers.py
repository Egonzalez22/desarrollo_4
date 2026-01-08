# -*- coding: utf-8 -*-
# from odoo import http


# class FePersonalizacion(http.Controller):
#     @http.route('/fe_personalizacion/fe_personalizacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fe_personalizacion/fe_personalizacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fe_personalizacion.listing', {
#             'root': '/fe_personalizacion/fe_personalizacion',
#             'objects': http.request.env['fe_personalizacion.fe_personalizacion'].search([]),
#         })

#     @http.route('/fe_personalizacion/fe_personalizacion/objects/<model("fe_personalizacion.fe_personalizacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fe_personalizacion.object', {
#             'object': obj
#         })
