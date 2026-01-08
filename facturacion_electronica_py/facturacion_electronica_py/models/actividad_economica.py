from odoo import _, api, fields, models


class ActividadEconomica(models.Model):
    _name = 'fe.actividad_economica'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código', required=True)
