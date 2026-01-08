from odoo import api, fields, models, exceptions, _
from datetime import date


class ReportCostoImportacion(models.AbstractModel):
    _name = 'report.interfaces_purchase.report_costo_importacion'

    @api.model
    def _get_report_values(self, docids, data=None):
        if len(docids) > 1:
            raise exceptions.UserError(_('Seleccionar solo un documento'))

        purchase = self.env['purchase.order'].browse(docids)[0]
        landeds = self.env['stock.landed.cost'].search([
            ("picking_ids", "in", [x.id for x in purchase.picking_ids]),
            ("state", "=", 'done')
        ], order="date desc")
        po_currency_id = purchase.currency_id

        last_land = landeds[0]
        reception = purchase.picking_ids[0]

        invoices = purchase.invoice_ids
        prod_list = []
        for line in purchase.order_line:
            standard_price = 0
            valuations = self.env["stock.valuation.layer"].search([
                ("product_id","=", line.product_id.id),
                ("create_date","<=", last_land.date),
                # ("stock_move_id","=", reception.id), # con move id no considera valor modificado manualmente
                ])
            if valuations:
                cost_val = sum(x.value for x in valuations)
                cost_qty = sum(x.quantity for x in valuations)
                standard_price = cost_val / cost_qty
            else:
                standard_price = line.product_id.standard_price

            prod_list.append({
                "default_code": line.product_id.default_code,
                "name": line.product_id.name,
                "price_unit": line.price_unit,
                "product_qty": line.product_qty,
                "standard_price": standard_price
            })

        return {
            "purchase": purchase,
            "po_currency_id": po_currency_id,
            "company_id": self.env.company,
            "pickings": purchase.picking_ids,
            "landeds": landeds ,
            "prod_list": prod_list ,
            "invoices": invoices
        }