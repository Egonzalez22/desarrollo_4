# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class tipo_cambio_picking(models.Model):
#     _name = 'tipo_cambio_picking.tipo_cambio_picking'
#     _description = 'tipo_cambio_picking.tipo_cambio_picking'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
