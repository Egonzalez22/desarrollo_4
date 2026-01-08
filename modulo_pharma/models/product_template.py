from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    metodo_asociado = fields.Boolean(string="Metodo Asociado")
