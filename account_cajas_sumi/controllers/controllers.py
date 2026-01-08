# -*- coding: utf-8 -*-
# from odoo import http


# class PresupuestoReportes(http.Controller):
#     @http.route('/presupuesto_reportes/presupuesto_reportes', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/presupuesto_reportes/presupuesto_reportes/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('presupuesto_reportes.listing', {
#             'root': '/presupuesto_reportes/presupuesto_reportes',
#             'objects': http.request.env['presupuesto_reportes.presupuesto_reportes'].search([]),
#         })

#     @http.route('/presupuesto_reportes/presupuesto_reportes/objects/<model("presupuesto_reportes.presupuesto_reportes"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('presupuesto_reportes.object', {
#             'object': obj
#         })
