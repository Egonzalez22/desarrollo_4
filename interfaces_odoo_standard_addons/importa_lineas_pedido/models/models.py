# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class importa_lineas_pedido(models.Model):
#     _name = 'importa_lineas_pedido.importa_lineas_pedido'
#     _description = 'importa_lineas_pedido.importa_lineas_pedido'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
