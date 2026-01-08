# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    oportunidad_moneda = fields.Many2one('res.currency', string="Moneda Oportunidad", default=155)
    oportunidad_monto = fields.Float(string="Monto Oportunidad")

    @api.onchange('oportunidad_moneda', 'oportunidad_monto')
    @api.depends('oportunidad_moneda', 'oportunidad_monto')
    def onchange_oportunidad(self):
        if self.oportunidad_moneda:
            monto = self.oportunidad_moneda._convert(self.oportunidad_monto, self.env.company.currency_id, self.env.company,
                                                     datetime.date.today())
            self.write({
                'expected_revenue': monto
            })

