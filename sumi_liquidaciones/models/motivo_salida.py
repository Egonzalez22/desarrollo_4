# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MotivoSalida(models.Model):
    _name = 'sumi_liquidaciones.motivo_salida'


    name = fields.Char(string="Motivo de Salida")
    active = fields.Boolean('Activo', default=True)