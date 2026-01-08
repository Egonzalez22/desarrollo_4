from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    tipo_cambio=fields.Float(string="Tipo de cambio",default=1,tracking=True)
    es_devolucion_compra=fields.Boolean(default=False,copy=False)
    
    