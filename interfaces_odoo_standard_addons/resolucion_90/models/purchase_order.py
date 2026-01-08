
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()

        # Pasamos el campo excluir_res90 del pedido de compra a la factura
        res['excluir_res90'] = self.partner_id.proveedor_facturador_electronico
        return res
