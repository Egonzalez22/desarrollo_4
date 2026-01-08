from odoo import fields, api, models, exceptions


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def gap_get_odoo_rate(self, company_currency, recon_currency, vals, other_line=None):
        # grupo_account_payment_tipo_cambio_compra_venta/models/account_move_line.py
        result = super(AccountMoveLine, self).gap_get_odoo_rate(company_currency, recon_currency, vals, other_line)

        def get_accounting_rate(vals):
            if company_currency.is_zero(vals["balance"]) or vals["currency"].is_zero(vals["amount_currency"]):
                return None
            else:
                return abs(vals["amount_currency"]) / abs(vals["balance"])

        if other_line.get("record") and other_line["record"].move_id:
            if other_line["record"].move_id.move_type == "entry" and other_line["record"].move_id.is_repartition_move:
                return get_accounting_rate(other_line)
        return result
