# -*- coding: utf-8 -*-
# from odoo import http


# class ReportesVentasCobranzas(http.Controller):
#     @http.route('/reportes_ventas_cobranzas/reportes_ventas_cobranzas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reportes_ventas_cobranzas/reportes_ventas_cobranzas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reportes_ventas_cobranzas.listing', {
#             'root': '/reportes_ventas_cobranzas/reportes_ventas_cobranzas',
#             'objects': http.request.env['reportes_ventas_cobranzas.reportes_ventas_cobranzas'].search([]),
#         })

#     @http.route('/reportes_ventas_cobranzas/reportes_ventas_cobranzas/objects/<model("reportes_ventas_cobranzas.reportes_ventas_cobranzas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reportes_ventas_cobranzas.object', {
#             'object': obj
#         })
