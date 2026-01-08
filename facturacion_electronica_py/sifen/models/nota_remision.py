from odoo import _, api, exceptions, fields, models


class NotasRemision(models.Model):
    _inherit = 'notas_remision_account.nota.remision'

    invoice_datetime = fields.Datetime(string="Fecha y Hora de Emisión", default=lambda self: fields.Datetime.now(), copy=False)
