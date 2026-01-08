from odoo import fields, api, models, exceptions


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_amount_residual_in_payment_group_currency(self, payment_type, active_payment_group_currency, fecha=fields.Date.today()):
        result = super(AccountMove, self)._get_amount_residual_in_payment_group_currency(payment_type, active_payment_group_currency, fecha)
        for this in self:
            amount_residual_in_payment_group_currency = this.amount_residual
            if not active_payment_group_currency:
                active_payment_group_currency = this.currency_id
            if this.currency_id != active_payment_group_currency:
                _convert = this.currency_id._convert
                if payment_type == "inbound":
                    _convert = this.currency_id._convert_tipo_cambio_comprador
                elif payment_type == "outbound":
                    _convert = this.currency_id._convert_tipo_cambio_vendedor
                amount_residual_in_payment_group_currency = _convert(
                    this.amount_residual,
                    active_payment_group_currency,
                    this.company_id,
                    fecha,
                )
            if this.active_payment_group_currency != active_payment_group_currency:
                this.active_payment_group_currency = active_payment_group_currency
            if this.amount_residual_in_payment_group_currency != amount_residual_in_payment_group_currency:
                this.amount_residual_in_payment_group_currency = amount_residual_in_payment_group_currency
        return result
