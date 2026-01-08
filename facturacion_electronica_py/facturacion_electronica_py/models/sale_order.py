from odoo import fields, api, models, exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    factura_anticipo = fields.Many2one('account.move', string="Factura de anticipo")
