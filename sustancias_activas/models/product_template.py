from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sustancias_activas_ids = fields.Many2many('sustancias_activas', string='Sustancias Activas')
