# -*- coding: utf-8 -*-
# from odoo import http


# class SaleProductVariantChoose(http.Controller):
#     @http.route('/sale_product_variant_choose/sale_product_variant_choose', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_product_variant_choose/sale_product_variant_choose/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_product_variant_choose.listing', {
#             'root': '/sale_product_variant_choose/sale_product_variant_choose',
#             'objects': http.request.env['sale_product_variant_choose.sale_product_variant_choose'].search([]),
#         })

#     @http.route('/sale_product_variant_choose/sale_product_variant_choose/objects/<model("sale_product_variant_choose.sale_product_variant_choose"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_product_variant_choose.object', {
#             'object': obj
#         })
