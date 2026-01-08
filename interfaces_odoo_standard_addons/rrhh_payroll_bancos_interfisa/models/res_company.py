from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    banco_interfisa_nro_cuenta = fields.Char(string='Nro Cuenta INTERFISA')
