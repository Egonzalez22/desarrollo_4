# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    valor_residual_porc = fields.Float(string='Valor residual %')

    # Cuando cambia el valor residual, se debe actualizar el valor residual en el activo
    @api.onchange('valor_residual_porc')
    def _onchange_valor_residual_porc(self):
        for record in self:
            if self.original_value:
                record.salvage_value = record.valor_residual_porc * record.original_value / 100
