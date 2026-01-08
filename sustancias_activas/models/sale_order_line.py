# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sustancias_ids = fields.Many2many('sustancias_activas', string='Sustancias Activas')


