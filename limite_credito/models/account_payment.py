from odoo import _, api, exceptions, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    es_diferido = fields.Boolean(string="Es diferido", compute="_compute_es_diferido", store=True)

    @api.depends('tipo_pago')
    def _compute_es_diferido(self):
        for record in self:
            if record.tipo_pago and record.tipo_pago == 'Cheque':
                record.es_diferido = record.fecha_vencimiento_cheque > record.fecha_cheque
            else:
                record.es_diferido = False
