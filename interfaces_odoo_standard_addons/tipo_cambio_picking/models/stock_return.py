from odoo import _, api, fields, models



class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    
    def _prepare_picking_default_values(self):
        vals=super(StockReturnPicking,self)._prepare_picking_default_values()
        if self.picking_id.location_id.usage=='supplier' and self.picking_id.location_dest_id.usage=='internal':
            vals['es_devolucion_compra']=True
        return vals
            


