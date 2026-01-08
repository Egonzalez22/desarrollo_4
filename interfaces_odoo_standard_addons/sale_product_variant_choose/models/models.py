# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class sale_product_variant_choose(models.Model):
#     _name = 'sale_product_variant_choose.sale_product_variant_choose'
#     _description = 'sale_product_variant_choose.sale_product_variant_choose'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
