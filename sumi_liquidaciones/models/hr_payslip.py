# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    motivo_salida_id = fields.Many2one('sumi_liquidaciones.motivo_salida', string="Motivo de salida")
    