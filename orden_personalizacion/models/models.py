# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class orden_pago_personalizacion(models.Model):
#     _name = 'orden_pago_personalizacion.orden_pago_personalizacion'
#     _description = 'orden_pago_personalizacion.orden_pago_personalizacion'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
