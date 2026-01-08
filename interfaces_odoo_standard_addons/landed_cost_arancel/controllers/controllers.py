# -*- coding: utf-8 -*-
# from odoo import http


# class LandedCostArancel(http.Controller):
#     @http.route('/landed_cost_arancel/landed_cost_arancel', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/landed_cost_arancel/landed_cost_arancel/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('landed_cost_arancel.listing', {
#             'root': '/landed_cost_arancel/landed_cost_arancel',
#             'objects': http.request.env['landed_cost_arancel.landed_cost_arancel'].search([]),
#         })

#     @http.route('/landed_cost_arancel/landed_cost_arancel/objects/<model("landed_cost_arancel.landed_cost_arancel"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('landed_cost_arancel.object', {
#             'object': obj
#         })
