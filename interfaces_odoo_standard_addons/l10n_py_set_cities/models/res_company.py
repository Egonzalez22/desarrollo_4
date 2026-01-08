from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    city_id = fields.Many2one('res.city', string="Ciudad", domain="[('state_id', '=', state_id)]")
