from odoo import _, api, fields, models



class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'


    vendor_bill_ids = fields.Many2many('account.move', string='Facturas de proveedor', copy=False, domain=[('move_type', '=', 'in_invoice')])