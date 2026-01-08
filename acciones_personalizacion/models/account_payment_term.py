from odoo import models, fields, api

from datetime import datetime, timedelta

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    control_bloqueo = fields.Boolean(string='Control para bloqueo')
    control_bloqueo_30_dias = fields.Boolean(string='Control para bloqueo de 30 Dias')
