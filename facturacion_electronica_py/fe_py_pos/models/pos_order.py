import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _prepare_invoice_vals(self):
        """
        Sobreescribimos el método para agregar los campos requeridos por la factura electrónica
        """
        try:
            res = super(PosOrder, self)._prepare_invoice_vals()

            # Si el diario es diario electronico, entonces agregamos los campos requeridos
            if self.session_id.config_id.invoice_journal_id.es_documento_electronico:
                data = {
                    "indicador_presencia": self.session_id.config_id.indicador_presencia or '1',
                    "iTipTra": self.session_id.config_id.iTipTra or '3',
                    "iTImp": "1",
                }
                # Si es out_refund, agregamos la factura asociada
                if self.refunded_order_ids.account_move:
                    data["nro_factura_asociada"] = self.refunded_order_ids.account_move.id
                    data["motivo_emision"] = '1'
                    data["tipo_documento"] = 'out_refund'

                res.update(data)

            return res
        except Exception as e:
            _logger.error("Error en _prepare_invoice_vals: %s" % str(e))
            raise e
