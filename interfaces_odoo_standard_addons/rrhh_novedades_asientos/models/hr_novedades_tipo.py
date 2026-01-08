# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hrNovedadesTipo(models.Model):
    _inherit = 'hr.novedades.tipo'

    cuentas_pagos_pendientes = fields.Boolean(string="Usar cuentas de pagos pendientes", default=False)


