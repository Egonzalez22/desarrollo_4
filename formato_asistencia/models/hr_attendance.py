import logging
from odoo import fields, api, models, exceptions
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
from datetime import datetime

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    

    input_marked_formatted = fields.Char(compute='_compute_input_marked_formatted', string='Entrada Marcada Hora Formateada', store=True)
    output_marked_formatted = fields.Char(compute='_compute_output_marked_formatted', string='Salida Marcada Horas Formateada', store=True)
    worked_hours_formatted_t = fields.Char(compute='_compute_worked_hours_formatted_t', string='Horas de Trabajo Formateadas', store=True)

    def convertToHours(self, float_time):
        t_mili = float_time * 3600000
        t_str = str(datetime.fromtimestamp(t_mili / 1000).time()).split(':')
        return ":".join([t_str[0], t_str[1]])
    
    @api.depends('entrada_marcada')
    def _compute_input_marked_formatted(self):
        for record in self:
            if record.entrada_marcada:
                record.input_marked_formatted = self.convertToHours(record.entrada_marcada)
            else:
                record.input_marked_formatted = ""
                
    @api.depends('salida_marcada')
    def _compute_output_marked_formatted(self):
        for record in self:
            if record.salida_marcada:
               record.output_marked_formatted = self.convertToHours(record.salida_marcada)
            else:
                record.output_marked_formatted = ""
                
                
    @api.depends('worked_hours')
    def _compute_worked_hours_formatted_t(self):
        for record in self:
            if record.worked_hours is not None:
                record.worked_hours_formatted_t = self.convertToHours(record.worked_hours)
            else:
                record.worked_hours_formatted_t = ""




