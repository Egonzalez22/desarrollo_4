from odoo import _, api, fields, models


class Meta(models.Model):
    _name = 'cuotas.meta'
    _description = 'Meta'
    
    name=fields.Char(string="Descripción")
    fecha_inicio=fields.Date(string="Fecha de inicio")
    fecha_fin=fields.Date(string="Fecha de fin")
    cuotas_ids=fields.One2many("cuotas.cuota","meta_id",string="Cuotas")
    currency_id=fields.Many2one("res.currency",string="Moneda",default=lambda self:self.env.company.currency_id,readonly=True)
    total_amount=fields.Monetary(string="Total meta",currency_field="currency_id",compute="compute_total")
    
    def compute_total(self):
        for i in self:
            if i.cuotas_ids:
                i.total_amount=sum(i.cuotas_ids.mapped('saldo_pagar_company_currency'))
            else:
                i.total_amount=0
