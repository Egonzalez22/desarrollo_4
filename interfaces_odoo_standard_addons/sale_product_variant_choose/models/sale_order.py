from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def button_seleccion_variantes(self):
        
        return {
                'view_mode': 'form',
                'res_model': 'sale.product.variant.choose',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': False,
                'context':{'default_order_id':self.id}
            }