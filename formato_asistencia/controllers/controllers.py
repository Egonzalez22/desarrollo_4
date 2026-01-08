# -*- coding: utf-8 -*-
# from odoo import http


# class FormatoAsistencia(http.Controller):
#     @http.route('/formato_asistencia/formato_asistencia', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/formato_asistencia/formato_asistencia/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('formato_asistencia.listing', {
#             'root': '/formato_asistencia/formato_asistencia',
#             'objects': http.request.env['formato_asistencia.formato_asistencia'].search([]),
#         })

#     @http.route('/formato_asistencia/formato_asistencia/objects/<model("formato_asistencia.formato_asistencia"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('formato_asistencia.object', {
#             'object': obj
#         })
