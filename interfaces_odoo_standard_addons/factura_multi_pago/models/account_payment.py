from odoo import fields, api, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_group_id = fields.Many2one('factura_multi_pago.payment_group', string='Grupo de pago')
