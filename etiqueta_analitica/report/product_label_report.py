# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import _, models
from odoo.exceptions import UserError


def _prepare_data(env, data):
    # change product ids by actual product object to get access to fields in xml template
    # we needed to pass ids because reports only accepts native python types (int, float, strings, ...)
    if data.get('active_model') == 'product.template':
        Product = env['product.template'].with_context(display_default_code=False)
    elif data.get('active_model') == 'product.product':
        Product = env['product.product'].with_context(display_default_code=False)
    else:
        raise UserError(_('Product model not defined, Please contact your administrator.'))

    total = 0
    qty_by_product_in = data.get('quantity_by_product')
    # search for products all at once, ordered by name desc since popitem() used in xml to print the labels
    # is LIFO, which results in ordering by product name in the report
    products = Product.search([('id', 'in', [int(p) for p in qty_by_product_in.keys()])], order='name desc')
    quantity_by_product = defaultdict(list)
    for product in products:
        q = qty_by_product_in[str(product.id)]
        quantity_by_product[product].append((product.barcode, q))
        total += q
    if data.get('custom_barcodes'):
        # we expect custom barcodes format as: {product: [(barcode, qty_of_barcode)]}
        for product, barcodes_qtys in data.get('custom_barcodes').items():
            quantity_by_product[Product.browse(int(product))] += (barcodes_qtys)
            total += sum(qty for _, qty in barcodes_qtys)

    layout_wizard = env['product.label.layout'].browse(data.get('layout_wizard'))
    if not layout_wizard:
        return {}

    # Desde el params obtenemos el ID del picking para pasar los datos que necesitamos
    picking_id = data.get('context').get('params').get('id')
    picking = env['stock.picking'].search([('id', '=', picking_id)], limit=1)

    result = {
        'quantity': quantity_by_product,
        'rows': layout_wizard.rows,
        'columns': layout_wizard.columns,
        'page_numbers': (total - 1) // (layout_wizard.rows * layout_wizard.columns) + 1,
        'price_included': data.get('price_included'),
        'extra_html': layout_wizard.extra_html,
        'picking': picking
    }

    return result



class ReportProductTemplateLabelDymoSinPrecio(models.AbstractModel):
    _name = 'report.ventas_custom.report_dymo_sinprecio'
    _description = 'Product Label Report Without Price'

    def _get_report_values(self, docids, data):
        print(data)
        print(docids)
        print("data")
        return _prepare_data(self.env, data)