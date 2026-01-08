from odoo import models, fields, api, tools
from dateutil.relativedelta import relativedelta


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    method_period = fields.Selection(selection_add=[('0', 'Días')], ondelete={'days': 'set default'})

    def _get_end_period_date(self, start_depreciation_date):
        # account_asset_days/models/account_asset.py
        result = super(AccountAsset, self)._get_end_period_date(start_depreciation_date=start_depreciation_date)
        if self.method_period == '0':
            return start_depreciation_date
        return result

    def _get_last_day_asset(self):
        # account_asset_days/models/account_asset.py
        result = super(AccountAsset, self)._get_last_day_asset()
        this = self.parent_id if self.parent_id else self
        if this.method_period == '0':
            return this.paused_prorata_date + relativedelta(days=this.method_number)
        return result

    @api.depends('method_number', 'method_period', 'prorata_computation_type')
    def _compute_lifetime_days(self):
        result = super(AccountAsset, self)._compute_lifetime_days()
        for asset in self:
            if asset.method_period == '0':
                if not asset.parent_id:
                    if asset.prorata_computation_type == 'daily_computation':
                        asset.asset_lifetime_days = (asset.prorata_date + relativedelta(days=asset.method_number) - asset.prorata_date).days
        return result

    def _compute_board_amount(self, residual_amount, period_start_date, period_end_date, days_already_depreciated,
                              days_left_to_depreciated, residual_declining, start_yearly_period=None, total_lifetime_left=None,
                              residual_at_compute=None, start_recompute_date=None):
        result = super(AccountAsset, self)._compute_board_amount(
            residual_amount=residual_amount,
            period_start_date=period_start_date,
            period_end_date=period_end_date,
            days_already_depreciated=days_already_depreciated,
            days_left_to_depreciated=days_left_to_depreciated,
            residual_declining=residual_declining,
            start_yearly_period=start_yearly_period,
            total_lifetime_left=total_lifetime_left,
            residual_at_compute=residual_at_compute,
            start_recompute_date=start_recompute_date,
        )
        if self.method_period == '0':
            if self.method == 'linear':
                days_until_period_end = self._get_delta_days(self.paused_prorata_date, period_end_date)
                days_before_period = self._get_delta_days(self.paused_prorata_date, period_start_date + relativedelta(days=-1))
                days_before_period = max(days_before_period, 0)  # if disposed before the beginning of the asset for example
                number_days = days_until_period_end - days_before_period
                if total_lifetime_left and tools.float_compare(total_lifetime_left, 0, 2) > 0:
                    computed_linear_amount = residual_amount - residual_at_compute * (
                            1 - self._get_delta_days(start_recompute_date, period_end_date) / (total_lifetime_left - 1)
                    )
                else:
                    computed_linear_amount = self._get_linear_amount(days_before_period, days_until_period_end, self.total_depreciable_value)
                amount = min(computed_linear_amount, residual_amount, key=abs)

                amount = max(amount, 0) if self.currency_id.compare_amounts(residual_amount, 0) > 0 else min(amount, 0)

                if abs(residual_amount) < abs(amount) or days_until_period_end >= self.asset_lifetime_days:
                    amount = residual_amount
                return number_days, self.currency_id.round(amount)

        return result
