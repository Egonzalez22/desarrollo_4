# -*- coding: utf-8 -*-
# from odoo import http


# class InformeAsistencias(http.Controller):
#     @http.route('/informe_asistencias/informe_asistencias/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/informe_asistencias/informe_asistencias/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('informe_asistencias.listing', {
#             'root': '/informe_asistencias/informe_asistencias',
#             'objects': http.request.env['informe_asistencias.informe_asistencias'].search([]),
#         })

#     @http.route('/informe_asistencias/informe_asistencias/objects/<model("informe_asistencias.informe_asistencias"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('informe_asistencias.object', {
#             'object': obj
#         })
