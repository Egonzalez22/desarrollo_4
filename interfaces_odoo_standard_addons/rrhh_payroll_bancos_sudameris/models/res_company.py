from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    MODALIDAD_PAGO = [
        ('20', 'Débito en Cta. Cte'),
        ('21', 'Débito Caja de Ahorro'),
    ]

    banco_sudameris_nro_cuenta = fields.Char(string='Nro Cuenta SUDAMERIS')
    banco_sudameris_cod_contrato = fields.Char(string='Nro Contrato SUDAMERIS')
    banco_sudameris_email_asociado = fields.Char(string='Email Asociado SUDAMERIS')

    sudameris_num_sucursal = fields.Integer(string="Numero de Sucursal")
    sudameris_cod_servicio = fields.Integer(string="Codigo de Servicio")
    
    sudameris_modalidad_pago = fields.Selection(
        selection=MODALIDAD_PAGO,
        string="Modalidad de Pago SUDAMERIS",
        default='20'
    )