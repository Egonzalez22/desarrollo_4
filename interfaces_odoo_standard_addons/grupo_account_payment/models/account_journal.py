from odoo import models, fields, api, exceptions


class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    diario_pagos_parciales = fields.Boolean("Diario para Pagos Parciales", default=False)
