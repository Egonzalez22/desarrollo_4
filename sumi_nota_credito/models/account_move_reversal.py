from odoo import models, fields, api

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    can_edit_date = fields.Boolean(compute='_compute_can_edit_date')

    @api.depends('company_id')
    def _compute_can_edit_date(self):
        for record in self:
            record.can_edit_date = self.env.user.has_group("sumi_nota_credito.group_nc_editar")
