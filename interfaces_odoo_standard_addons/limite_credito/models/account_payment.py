from odoo import _, api, exceptions, fields, models
from datetime import date


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    es_diferido = fields.Boolean(string="Es diferido", compute="_compute_es_diferido", store=True)

    @api.depends('tipo_pago','fecha_vencimiento_cheque','fecha_cheque')
    def _compute_es_diferido(self):
        for record in self:
            if record.tipo_pago == 'Cheque' and isinstance(record.fecha_vencimiento_cheque, date) and isinstance(record.fecha_cheque, date):
                record.es_diferido = record.fecha_vencimiento_cheque > record.fecha_cheque
            else:
                record.es_diferido = False
