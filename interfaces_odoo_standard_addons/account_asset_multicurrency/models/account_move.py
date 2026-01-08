from odoo import models, fields, api, tools


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('line_ids.balance')
    def _compute_depreciation_value(self):
        # account_asset_multicurrency/models/account_move.py
        result = super(AccountMove, self)._compute_depreciation_value()
        for move in self:
            asset = move.asset_id or move.reversed_entry_id.asset_id  # reversed moves are created before being assigned to the asset
            if asset:
                account_internal_group = 'income' if asset.asset_type == 'sale' else 'expense'
                asset_depreciation = sum(
                    move.line_ids.filtered(
                        lambda l:
                        l.account_id.internal_group == account_internal_group or
                        l.account_id == asset.account_depreciation_expense_id
                    ).mapped('amount_currency')
                ) * (-1 if asset.asset_type == 'sale' else 1)
                # Special case of closing entry - only disposed assets of type 'purchase' should match this condition
                # The condition on len(move.line_ids) is to avoid the case where there is only one depreciation move, and it is not a disposal move
                # The condition will be matched because a disposal move from a disposal move will always have more than 2 lines, unlike a normal depreciation move
                if any(
                        line.account_id == asset.account_asset_id
                        and tools.float_compare(-line.balance, asset.original_value, precision_rounding=asset.currency_id.rounding) == 0
                        for line in move.line_ids
                ) and len(move.line_ids) > 2:
                    asset_depreciation = (
                            asset.original_value
                            - asset.salvage_value
                            - (
                                move.line_ids[1].debit if asset.original_value > 0 else move.line_ids[1].credit
                            ) * (-1 if asset.original_value < 0 else 1)
                    )
            else:
                asset_depreciation = 0
            move.depreciation_value = asset_depreciation
        return result

    def _autopost_draft_entries(self):
        # account_asset_multicurrency/models/account_move.py
        moves = self.search([
            ('state', '=', 'draft'),
            ('date', '<=', fields.Date.context_today(self)),
            ('auto_post', '!=', 'no'),
            ('to_check', '=', False),
        ], limit=100)
        for move in moves.filtered(lambda x: x.asset_id or x.reversed_entry_id.asset_id):
            currency_rate = move.currency_id._get_conversion_rate(
                move.currency_id,
                move.company_id.currency_id,
                move.company_id,
                (move.invoice_date or move.date or fields.date.today())
            )
            for line in move.invoice_line_ids:
                if currency_rate and line.currency_rate != 1 / currency_rate:
                    line.with_context(check_move_validity=False).currency_rate = 1 / currency_rate
                line.with_context(check_move_validity=False).balance = line.company_id.currency_id.round(line.amount_currency / line.currency_rate)
        return super(AccountMove, self)._autopost_draft_entries()
