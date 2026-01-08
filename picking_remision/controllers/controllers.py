# -*- coding: utf-8 -*-
# from odoo import http


# class PickingRemision(http.Controller):
#     @http.route('/picking_remision/picking_remision/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/picking_remision/picking_remision/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('picking_remision.listing', {
#             'root': '/picking_remision/picking_remision',
#             'objects': http.request.env['picking_remision.picking_remision'].search([]),
#         })

#     @http.route('/picking_remision/picking_remision/objects/<model("picking_remision.picking_remision"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('picking_remision.object', {
#             'object': obj
#         })
