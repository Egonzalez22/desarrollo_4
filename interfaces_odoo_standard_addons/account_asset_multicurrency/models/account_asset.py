from odoo import models, fields, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    @api.model_create_multi
    def create(self, vals_list):
        # account_asset_multicurrency/models/account_asset.py
        result = super(AccountAsset, self).create(vals_list)
        for i, vals in enumerate(vals_list):
            if 'currency_id' in vals:
                result[i].currency_id = vals['currency_id']
        return result
