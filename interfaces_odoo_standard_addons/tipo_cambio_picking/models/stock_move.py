from odoo import _, api, fields, models
from odoo.tools.float_utils import float_round, float_is_zero, float_compare
from collections import defaultdict

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.origin_returned_move_id or not self.purchase_line_id or not self.product_id.id:
            return super(StockMove, self)._get_price_unit()
        price_unit_prec = self.env['decimal.precision'].precision_get(
            'Product Price')
        line = self.purchase_line_id
        order = line.order_id
        received_qty = line.qty_received
        if self.state == 'done':
            received_qty -= self.product_uom._compute_quantity(
                self.quantity_done, line.product_uom, rounding_method='HALF-UP')
        if float_compare(line.qty_invoiced, received_qty, precision_rounding=line.product_uom.rounding) > 0:
            move_layer = line.move_ids.stock_valuation_layer_ids
            invoiced_layer = line.invoice_lines.stock_valuation_layer_ids
            receipt_value = sum(move_layer.mapped('value')) + \
                sum(invoiced_layer.mapped('value'))
            invoiced_value = 0
            invoiced_qty = 0
            for invoice_line in line.invoice_lines:
                if invoice_line.tax_ids:
                    invoiced_value += invoice_line.tax_ids.with_context(round=False).compute_all(
                        invoice_line.price_unit, currency=invoice_line.account_id.currency_id or invoice_line.currency_id, quantity=invoice_line.quantity)['total_void']
                else:
                    invoiced_value += invoice_line.price_unit * invoice_line.quantity
                invoiced_qty += invoice_line.product_uom_id._compute_quantity(
                    invoice_line.quantity, line.product_id.uom_id)
            # TODO currency check
            remaining_value = invoiced_value - receipt_value
            # TODO qty_received in product uom
            remaining_qty = invoiced_qty - \
                line.product_uom._compute_quantity(
                    received_qty, line.product_id.uom_id)
            price_unit = float_round(
                remaining_value / remaining_qty, precision_digits=price_unit_prec)
        else:
            price_unit = line.price_unit
            if line.taxes_id:
                qty = line.product_qty or 1
                price_unit = line.taxes_id.with_context(round=False).compute_all(
                    price_unit, currency=line.order_id.currency_id, quantity=qty)['total_void']
                price_unit = float_round(
                    price_unit / qty, precision_digits=price_unit_prec)
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            # The date must be today, and not the date of the move since the move move is still
            # in assigned state. However, the move date is the scheduled date until move is
            # done, then date of actual move processing. See:
            # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
            if order.company_id.currency_id.name == 'PYG' and self.picking_id.tipo_cambio > 0 and self._is_in():
                price_unit = price_unit * self.picking_id.tipo_cambio
            else:
                price_unit = order.currency_id._convert(
                    price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)
        return price_unit


    def _create_out_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_out_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
            if float_is_zero(forced_quantity or valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                continue
            svl_vals = move.product_id._prepare_out_svl_vals(forced_quantity or valued_quantity, move.company_id)
            if move.picking_id.es_devolucion_compra:
                precio_unitario=move._get_price_unit()
                svl_vals['unit_cost']=precio_unitario
                svl_vals['value']=precio_unitario * svl_vals['quantity']
                product_svls=self.env['stock.valuation.layer'].sudo().search([('product_id','=',move.product_id.id)])
                total_value=abs(sum(product_svls.filtered(lambda x:x.company_id==self.env.company).mapped('value'))) + svl_vals['value']
                total_qty=abs(sum(product_svls.filtered(lambda x:x.company_id==self.env.company).mapped('quantity'))) + svl_vals['quantity']
                if total_qty>0:
                    new_std_price=total_value/total_qty
                    move.product_id.with_company(move.company_id.id).with_context(disable_auto_svl=True).sudo().write({'standard_price': new_std_price})
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals['description'] = 'Correction of %s (modification of past move)' % (move.picking_id.name or move.name)
            svl_vals['description'] += svl_vals.pop('rounding_adjustment', '')
            svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
    
    
    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        """ Overridden from stock_account to support amount_currency on valuation lines generated from po
        """
        self.ensure_one()

        rslt = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description)
        purchase_currency = self.purchase_line_id.currency_id
        company_currency = self.company_id.currency_id
        if not self.purchase_line_id or purchase_currency == company_currency:
            return rslt
        svl = self.env['stock.valuation.layer'].browse(svl_id)
        if not svl.account_move_line_id:
            # rslt['credit_line_vals']['amount_currency'] = company_currency._convert(
            #     rslt['credit_line_vals']['balance'],
            #     purchase_currency,
            #     self.company_id,
            #     self.date
            # )
            rslt['credit_line_vals']['amount_currency'] =self.purchase_line_id.price_total * -1
            # rslt['debit_line_vals']['amount_currency'] = company_currency._convert(
            #     rslt['debit_line_vals']['balance'],
            #     purchase_currency,
            #     self.company_id,
            #     self.date
            # )
            rslt['debit_line_vals']['amount_currency'] =self.purchase_line_id.price_total
            rslt['debit_line_vals']['currency_id'] = purchase_currency.id
            rslt['credit_line_vals']['currency_id'] = purchase_currency.id
        else:
            rslt['credit_line_vals']['amount_currency'] = 0
            rslt['debit_line_vals']['amount_currency'] = 0
            rslt['debit_line_vals']['currency_id'] = purchase_currency.id
            rslt['credit_line_vals']['currency_id'] = purchase_currency.id
            if not svl.price_diff_value:
                return rslt
            # The idea is to force using the company currency during the reconciliation process
            rslt['debit_line_vals_curr'] = {
                'name': _("Currency exchange rate difference"),
                'product_id': self.product_id.id,
                'quantity': 0,
                'product_uom_id': self.product_id.uom_id.id,
                'partner_id': partner_id,
                'balance': 0,
                'account_id': debit_account_id,
                'currency_id': purchase_currency.id,
                'amount_currency': -svl.price_diff_value,
            }
            rslt['credit_line_vals_curr'] = {
                'name': _("Currency exchange rate difference"),
                'product_id': self.product_id.id,
                'quantity': 0,
                'product_uom_id': self.product_id.uom_id.id,
                'partner_id': partner_id,
                'balance': 0,
                'account_id': credit_account_id,
                'currency_id': purchase_currency.id,
                'amount_currency': svl.price_diff_value,
            }
        return rslt