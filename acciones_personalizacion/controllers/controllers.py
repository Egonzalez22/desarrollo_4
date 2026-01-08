# -*- coding: utf-8 -*-
# from odoo import http


# class AccionesPersonalizacion(http.Controller):
#     @http.route('/acciones_personalizacion/acciones_personalizacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/acciones_personalizacion/acciones_personalizacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('acciones_personalizacion.listing', {
#             'root': '/acciones_personalizacion/acciones_personalizacion',
#             'objects': http.request.env['acciones_personalizacion.acciones_personalizacion'].search([]),
#         })

#     @http.route('/acciones_personalizacion/acciones_personalizacion/objects/<model("acciones_personalizacion.acciones_personalizacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('acciones_personalizacion.object', {
#             'object': obj
#         })
