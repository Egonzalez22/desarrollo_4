# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class City(models.Model):
    _inherit = 'res.city'

    code = fields.Integer('Código')
    district_id = fields.Many2one('res.district', 'Distrito', domain="[('state_id', '=', state_id)]")
