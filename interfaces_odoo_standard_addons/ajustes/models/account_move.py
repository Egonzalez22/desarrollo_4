from odoo import models,api,fields,exceptions

class AccountMove(models.Model):
    _inherit='account.move'


    @api.depends('name', 'journal_id')
    def _compute_made_sequence_hole(self):
        for i in self:
            i.made_sequence_hole=False

