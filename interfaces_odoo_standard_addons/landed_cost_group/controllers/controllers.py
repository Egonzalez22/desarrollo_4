# -*- coding: utf-8 -*-
# from odoo import http


# class LandedCostGroup(http.Controller):
#     @http.route('/landed_cost_group/landed_cost_group', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/landed_cost_group/landed_cost_group/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('landed_cost_group.listing', {
#             'root': '/landed_cost_group/landed_cost_group',
#             'objects': http.request.env['landed_cost_group.landed_cost_group'].search([]),
#         })

#     @http.route('/landed_cost_group/landed_cost_group/objects/<model("landed_cost_group.landed_cost_group"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('landed_cost_group.object', {
#             'object': obj
#         })
