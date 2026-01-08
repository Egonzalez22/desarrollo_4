from odoo import models, api, fields, exceptions


class AccountTax(models.Model):
    _inherit = 'account.tax'

    porcentaje_sobre_base = fields.Float(string='Porcentaje aplicado sobre el monto base (Solo útil para impresión de Facturas)', default=100)
