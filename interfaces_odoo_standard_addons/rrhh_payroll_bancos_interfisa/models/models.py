# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class txt_interfisa(models.Model):
#     _name = 'txt_interfisa.txt_interfisa'
#     _description = 'txt_interfisa.txt_interfisa'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
