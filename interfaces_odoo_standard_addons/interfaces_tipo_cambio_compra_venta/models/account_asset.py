from odoo import fields, models, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    def _recompute_board(self, start_depreciation_date=False):
        # interfaces_tipo_cambio_compra_venta/models/account_asset.py
        result = super(AccountAsset, self)._recompute_board(start_depreciation_date=start_depreciation_date)
        for this in result:
            currency_rate = self.currency_id._get_conversion_rate(
                self.currency_id,
                self.company_id.currency_id,
                self.company_id,
                (this.get('date') or fields.date.today())
            )
            this['currency_rate'] = currency_rate
        return result
