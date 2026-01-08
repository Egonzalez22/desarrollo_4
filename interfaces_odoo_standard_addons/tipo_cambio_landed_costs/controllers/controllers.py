# -*- coding: utf-8 -*-
# from odoo import http


# class TipoCambioLandedCosts(http.Controller):
#     @http.route('/tipo_cambio_landed_costs/tipo_cambio_landed_costs', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tipo_cambio_landed_costs/tipo_cambio_landed_costs/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tipo_cambio_landed_costs.listing', {
#             'root': '/tipo_cambio_landed_costs/tipo_cambio_landed_costs',
#             'objects': http.request.env['tipo_cambio_landed_costs.tipo_cambio_landed_costs'].search([]),
#         })

#     @http.route('/tipo_cambio_landed_costs/tipo_cambio_landed_costs/objects/<model("tipo_cambio_landed_costs.tipo_cambio_landed_costs"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tipo_cambio_landed_costs.object', {
#             'object': obj
#         })
