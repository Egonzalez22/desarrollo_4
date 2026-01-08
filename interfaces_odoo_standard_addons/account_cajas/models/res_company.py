from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_caja_sessions = fields.Boolean(string='Habilitar Sesiones de Caja', default=True)
    caja_sessions_inbound_control = fields.Boolean(string='Control de sesiones de caja para pagos entrantes', default=True)
    caja_sessions_outbound_control = fields.Boolean(string='Control de sesiones de caja para pagos salientes', default=False)
