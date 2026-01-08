from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    hora_inicio = fields.Float(string="Hora de Inicio")
    hora_fin = fields.Float(string="Hora de Fin")

    @api.constrains('hora_inicio', 'hora_fin')
    def _constrains_horas(self):
        for record in self:

            if record.hora_inicio == 0 and record.hora_fin == 0:
                return

            if record.hora_fin < record.hora_inicio:
                raise UserError('La hora de inicio no puede ser posterior a la hora de fin')
                
            record.unit_amount = record.hora_fin - record.hora_inicio