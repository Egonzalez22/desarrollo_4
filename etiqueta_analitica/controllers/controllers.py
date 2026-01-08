# -*- coding: utf-8 -*-
# from odoo import http


# class VentasCamposPersonalizados(http.Controller):
#     @http.route('/ventas_campos_personalizados/ventas_campos_personalizados', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ventas_campos_personalizados/ventas_campos_personalizados/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ventas_campos_personalizados.listing', {
#             'root': '/ventas_campos_personalizados/ventas_campos_personalizados',
#             'objects': http.request.env['ventas_campos_personalizados.ventas_campos_personalizados'].search([]),
#         })

#     @http.route('/ventas_campos_personalizados/ventas_campos_personalizados/objects/<model("ventas_campos_personalizados.ventas_campos_personalizados"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ventas_campos_personalizados.object', {
#             'object': obj
#         })
