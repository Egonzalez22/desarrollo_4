# -*- coding: utf-8 -*-
# from odoo import http


# class ReporteArqueo(http.Controller):
#     @http.route('/reporte_arqueo/reporte_arqueo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reporte_arqueo/reporte_arqueo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('reporte_arqueo.listing', {
#             'root': '/reporte_arqueo/reporte_arqueo',
#             'objects': http.request.env['reporte_arqueo.reporte_arqueo'].search([]),
#         })

#     @http.route('/reporte_arqueo/reporte_arqueo/objects/<model("reporte_arqueo.reporte_arqueo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reporte_arqueo.object', {
#             'object': obj
#         })
