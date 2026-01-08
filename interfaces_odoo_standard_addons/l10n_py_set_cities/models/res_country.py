from odoo import fields, api, models, exceptions


class ResCountry(models.Model):
    _inherit = 'res.country'

    code_alpha3 = fields.Char('Código ISO-3166 Alpha-3', required=False)
