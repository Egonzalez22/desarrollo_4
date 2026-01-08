from odoo import api, fields, models


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    codigo_cliente = fields.Char(string='Codigo Cliente')
