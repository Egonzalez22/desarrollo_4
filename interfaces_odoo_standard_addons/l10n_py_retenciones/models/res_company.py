from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    es_agente_retencion=fields.Boolean(string="Es agente de retención",default=False)
    tipo_agente_retencion=fields.Selection(string="Tipo de agente",selection=[('designado','Designado por DNIT'),('exportador','Exportador')])
    