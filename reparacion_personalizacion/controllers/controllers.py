# -*- coding: utf-8 -*-
# from odoo import http


# class ReparacionPersonalizacion(http.Controller):
#     @http.route('/reparacion_personalizacion/reparacion_personalizacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reparacion_personalizacion/reparacion_personalizacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('reparacion_personalizacion.listing', {
#             'root': '/reparacion_personalizacion/reparacion_personalizacion',
#             'objects': http.request.env['reparacion_personalizacion.reparacion_personalizacion'].search([]),
#         })

#     @http.route('/reparacion_personalizacion/reparacion_personalizacion/objects/<model("reparacion_personalizacion.reparacion_personalizacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reparacion_personalizacion.object', {
#             'object': obj
#         })
