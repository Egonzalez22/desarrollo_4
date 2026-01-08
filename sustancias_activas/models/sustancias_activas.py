# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class SustanciasActivas(models.Model):
    _name = 'sustancias_activas'

    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    name = fields.Char(string='Nombre')
    lod = fields.Char(string='LOD')
    intervalo_referencia = fields.Char(string='Intervalo de Referencia')
    u_unidad_loq = fields.Char(string='Unidad LOQ')
    u_loq = fields.Char(string='LOQ')
    referencia = fields.Char(string='Referencia')