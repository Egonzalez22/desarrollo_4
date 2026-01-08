# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class District(models.Model):
    _name = 'res.district'
    _description = 'Distritos'
    _order = 'name'

    name = fields.Char("Nombre", required=True, translate=True)
    code = fields.Char(string="Código", required=True)
    country_id = fields.Many2one('res.country', string='País', required=True, related="state_id.country_id")
    state_id = fields.Many2one('res.country.state', 'Departamento', domain="[('country_id', '=', country_id)]")
