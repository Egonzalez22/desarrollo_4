# -*- coding: utf-8 -*-
# from odoo import http


# class TipoCambioPicking(http.Controller):
#     @http.route('/tipo_cambio_picking/tipo_cambio_picking', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tipo_cambio_picking/tipo_cambio_picking/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tipo_cambio_picking.listing', {
#             'root': '/tipo_cambio_picking/tipo_cambio_picking',
#             'objects': http.request.env['tipo_cambio_picking.tipo_cambio_picking'].search([]),
#         })

#     @http.route('/tipo_cambio_picking/tipo_cambio_picking/objects/<model("tipo_cambio_picking.tipo_cambio_picking"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tipo_cambio_picking.object', {
#             'object': obj
#         })
