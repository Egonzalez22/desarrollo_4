# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class landed_cost_arancel(models.Model):
#     _name = 'landed_cost_arancel.landed_cost_arancel'
#     _description = 'landed_cost_arancel.landed_cost_arancel'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
