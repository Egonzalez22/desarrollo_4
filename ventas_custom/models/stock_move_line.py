from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    nro_lote = fields.Char(string='Nro. Lote')
    fecha_vencimiento_lote = fields.Date(string='Fecha Vencimiento')
    cantidad_impresiones = fields.Integer(string='Cantidad Impresiones', default=1)
    codigo_muestra = fields.Char(string='Código Muestra')
    observaciones = fields.Char(string='Observaciones')