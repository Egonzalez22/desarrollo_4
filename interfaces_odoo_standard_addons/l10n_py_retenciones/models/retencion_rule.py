from odoo import _, api, fields, models



class RetencionRule(models.Model):
    _name = 'retencion.rule'
    _description = 'Regla de retencion'
    
    tax_id=fields.Many2one("account.tax",string="Impuesto",domain=[('type_tax_use','=','purchase')])
    company_id=fields.Many2one("res.company",string="Compañia")
    porcentaje=fields.Float(string="Porcentaje de retención")
    tipo_agente=fields.Selection(string="Tipo de agente",selection=[('designado','Designado por DNIT'),('exportador','Exportador')])
    tipo_retencion=fields.Selection(string="Tipo de retencion",selection=[('IVA','IVA'),('RENTA','RENTA')])
    fecha_inicio=fields.Date(string="Inicio de vigencia")
    fecha_fin=fields.Date(string="Fin de vigencia")
    