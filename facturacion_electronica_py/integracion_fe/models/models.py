# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class integracion_fe(models.Model):
#     _name = 'integracion_fe.integracion_fe'
#     _description = 'integracion_fe.integracion_fe'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
