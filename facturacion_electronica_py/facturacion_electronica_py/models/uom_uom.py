from odoo import fields, api, models, exceptions


class UomUom(models.Model):
    _inherit = 'uom.uom'

    cod_set = fields.Integer(string="Código para Factura Electrónica")
    des_set = fields.Char(string="Descripción para Factura Electrónica")
