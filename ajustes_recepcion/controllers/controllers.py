# -*- coding: utf-8 -*-
# from odoo import http


# class AjustesRecepcion(http.Controller):
#     @http.route('/ajustes_recepcion/ajustes_recepcion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ajustes_recepcion/ajustes_recepcion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ajustes_recepcion.listing', {
#             'root': '/ajustes_recepcion/ajustes_recepcion',
#             'objects': http.request.env['ajustes_recepcion.ajustes_recepcion'].search([]),
#         })

#     @http.route('/ajustes_recepcion/ajustes_recepcion/objects/<model("ajustes_recepcion.ajustes_recepcion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ajustes_recepcion.object', {
#             'object': obj
#         })
