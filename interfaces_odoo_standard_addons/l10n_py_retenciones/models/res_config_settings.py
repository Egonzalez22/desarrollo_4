from odoo import _, api, fields, models



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    ret_monto_minimo=fields.Float(string="Monto mínimo para retenciones",config_parameter="ret_monto_minimo")
    
