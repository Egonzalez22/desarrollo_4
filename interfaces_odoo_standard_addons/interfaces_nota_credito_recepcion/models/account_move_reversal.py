from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move)

        # Si move_type es in_invoice, sobreescribimos el campo ref, caso contrario sigue el flujo normal
        if move.move_type == 'in_invoice':
            res['ref'] = move.ref

        return res
