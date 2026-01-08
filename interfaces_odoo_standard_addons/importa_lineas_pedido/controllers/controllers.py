# -*- coding: utf-8 -*-
# from odoo import http


# class ImportaLineasPedido(http.Controller):
#     @http.route('/importa_lineas_pedido/importa_lineas_pedido', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/importa_lineas_pedido/importa_lineas_pedido/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('importa_lineas_pedido.listing', {
#             'root': '/importa_lineas_pedido/importa_lineas_pedido',
#             'objects': http.request.env['importa_lineas_pedido.importa_lineas_pedido'].search([]),
#         })

#     @http.route('/importa_lineas_pedido/importa_lineas_pedido/objects/<model("importa_lineas_pedido.importa_lineas_pedido"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('importa_lineas_pedido.object', {
#             'object': obj
#         })
