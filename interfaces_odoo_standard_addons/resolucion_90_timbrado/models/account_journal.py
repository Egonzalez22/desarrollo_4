from odoo import models,fields,api,exceptions


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    timbrado_autofactura=fields.Boolean(string="Timbrado Autofactura",default=False,copy=False,help="Para procesar autofacturas con el timnbrado indicado")