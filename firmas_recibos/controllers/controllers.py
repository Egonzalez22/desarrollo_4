# -*- coding: utf-8 -*-
# from odoo import http


# class FirmasRecibos(http.Controller):
#     @http.route('/firmas_recibos/firmas_recibos', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/firmas_recibos/firmas_recibos/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('firmas_recibos.listing', {
#             'root': '/firmas_recibos/firmas_recibos',
#             'objects': http.request.env['firmas_recibos.firmas_recibos'].search([]),
#         })

#     @http.route('/firmas_recibos/firmas_recibos/objects/<model("firmas_recibos.firmas_recibos"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('firmas_recibos.object', {
#             'object': obj
#         })
