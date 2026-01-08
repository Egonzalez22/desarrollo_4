from odoo import models,api,fields,exceptions

class AccountJournal(models.Model):
    _inherit='account.journal'

    def _compute_has_sequence_holes(self):
        for i in self:
            i.has_sequence_holes=False
