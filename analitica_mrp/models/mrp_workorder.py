from odoo import _, api, fields, models




class MRPWorkOrder(models.Model):
    _inherit = 'mrp.workorder'
    
    
    def button_iniciar(self):
        for record in self:
            record.button_start()
            
    def button_hecho(self):
        for record in self:
            record.button_finish()
            
