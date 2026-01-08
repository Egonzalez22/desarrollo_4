# -*- coding: utf-8 -*-

from odoo import models, fields, api, release


class ProductCategory(models.Model):
    _inherit = "product.category"

    excluir_reporte_compraventa = fields.Boolean("Excluir productos del reporte Compra-Venta", default=False)
