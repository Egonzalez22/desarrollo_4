from odoo import models, fields, api, exceptions
import datetime


class HREmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    MODALIDAD_PAGO = [
        ('20', 'Débito en Cta. Cte'),
        ('21', 'Débito Caja de Ahorro'),
    ]

    modalidad_pago_sudamedis = fields.Selection(
        selection=MODALIDAD_PAGO,
        string="Modalidad de Pago SUDAMERIS",
        default='20'
    )