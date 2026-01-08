from odoo import fields, api, models, exceptions


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    payment_repartition_origin_invoice_id = fields.Many2one('account.move')
