# -*- coding: utf-8 -*-
# from odoo import http


# class MuestraReports(http.Controller):
#     @http.route('/muestra_reports/muestra_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/muestra_reports/muestra_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('muestra_reports.listing', {
#             'root': '/muestra_reports/muestra_reports',
#             'objects': http.request.env['muestra_reports.muestra_reports'].search([]),
#         })

#     @http.route('/muestra_reports/muestra_reports/objects/<model("muestra_reports.muestra_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('muestra_reports.object', {
#             'object': obj
#         })
