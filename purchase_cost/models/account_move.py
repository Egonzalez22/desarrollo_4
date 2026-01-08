from odoo import _, api, fields, models,exceptions
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _apply_price_difference(self):
        for line in self:
            svl_vals_list = []
            aml_vals_list = []
            if line.move_type == 'in_invoice':
                line = line.with_company(line.company_id)
                po_line = line.purchase_line_id
                uom = line.product_uom_id or line.product_id.uom_id

                # Don't create value for more quantity than received
                quantity = po_line.qty_received - (po_line.qty_invoiced - line.quantity)
                quantity = max(min(line.quantity, quantity), 0)
                if float_is_zero(quantity, precision_rounding=uom.rounding):
                    continue

                layers = line._get_valued_in_moves().stock_valuation_layer_ids.filtered(
                    lambda svl: svl.product_id == line.product_id and not svl.stock_valuation_layer_id)
                if not layers:
                    continue

                if not line.move_id.freeze_currency_rate:
                    new_svl_vals_list, new_aml_vals_list = line._generate_price_difference_vals(layers)
                else:
                    new_svl_vals_list = []
                    new_aml_vals_list = []
                svl_vals_list += new_svl_vals_list
                aml_vals_list += new_aml_vals_list
            if svl_vals_list or aml_vals_list:
                raise UserError(
                    "Existen diferencias de precio en la factura de compra. Por favor, revise los valores antes de continuar."
                )

        return super()._apply_price_difference()