from odoo import api, fields, models


class QualityPoint(models.Model):
    _inherit = 'quality.point'

    fecha_inicio = fields.Date(string='Fecha de inicio')
    fecha_finalizacion = fields.Date(string='Fecha de finalización')
