from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_create_landed_costs(self):
        """Create a `stock.landed.cost` record associated to the account move of `self`, each
        `stock.landed.costs` lines mirroring the current `account.move.line` of self.
        """
        self.ensure_one()
        landed_costs_lines = self.line_ids.filtered(lambda line: line.is_landed_costs_line)
        balance = abs(self.line_ids[0].balance)
        amount_currency = abs(self.line_ids[0].amount_currency)
        if balance > 0 and amount_currency > 0:
            currency_rate = balance / amount_currency
        else:
            currency_rate = 1
        
        landed_costs = self.env['stock.landed.cost'].create({
            'vendor_bill_id': self.id,
            'cost_lines': [(0, 0, {
                'product_id': l.product_id.id,
                'name': l.product_id.name,
                'account_id': l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id,
                #'price_unit': l.currency_id._convert(l.price_subtotal, l.company_currency_id, l.company_id, l.move_id.date),
                'price_unit':l.price_subtotal * currency_rate,
                'split_method': l.product_id.split_method_landed_cost or 'equal',
            }) for l in landed_costs_lines],
        })
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])
