from datetime import datetime

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    text_acreditado = fields.Text(string='Texto Acreditado')
    logo_acreditado = fields.Image(string="Logo Acreditado") 

