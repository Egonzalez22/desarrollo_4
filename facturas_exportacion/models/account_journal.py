from odoo import models, fields, api, exceptions


class AccountJournal(models.Model):
    _inherit = "account.journal"
    es_factura_exportacion = fields.Boolean("Es factura de exportación", default=False)
