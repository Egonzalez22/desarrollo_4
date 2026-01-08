# -*- coding: utf-8 -*-
# from odoo import http


# class OrdenPagoPersonalizacion(http.Controller):
#     @http.route('/orden_pago_personalizacion/orden_pago_personalizacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/orden_pago_personalizacion/orden_pago_personalizacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('orden_pago_personalizacion.listing', {
#             'root': '/orden_pago_personalizacion/orden_pago_personalizacion',
#             'objects': http.request.env['orden_pago_personalizacion.orden_pago_personalizacion'].search([]),
#         })

#     @http.route('/orden_pago_personalizacion/orden_pago_personalizacion/objects/<model("orden_pago_personalizacion.orden_pago_personalizacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('orden_pago_personalizacion.object', {
#             'object': obj
#         })
