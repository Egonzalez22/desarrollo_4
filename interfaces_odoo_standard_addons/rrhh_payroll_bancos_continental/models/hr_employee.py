from odoo import api, fields, models


class HREmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    banco_continental_tipo_cuenta = fields.Selection([('CC', 'Cuenta Corriente'), ('AHO', 'Caja de Ahorro')], string='Tipo de Cuenta CONTINENTAL')
