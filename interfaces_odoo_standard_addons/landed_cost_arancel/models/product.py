from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    es_derecho_aduanero = fields.Boolean(
        string="Es un derecho aduanero", default=False, copy=False)
    porcentaje_arancel = fields.Float(string="Arancel aduanero", default=0)
