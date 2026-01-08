import logging
from odoo import fields, api, models, exceptions
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
from datetime import datetime

class RrhhAsistenciasMarcaciones(models.Model):
    _inherit = 'rrhh_asistencias.marcaciones'
    
    hours_formatted_t = fields.Char(compute='_compute_hours_formatted_t', string='Horas Formateadas', store=True)

    def convertToHours(self, float_time):
        t_mili = float_time * 3600000
        t_str = str(datetime.fromtimestamp(t_mili / 1000).time()).split(':')
        return ":".join([t_str[0], t_str[1]])
    
    
    @api.depends('hora')
    def _compute_hours_formatted_t(self):
        for record in self:
            if record.hora is not None:
                record.hours_formatted_t = self.convertToHours(record.hora)
            else:
                record.hours_formatted_t = ""