from odoo import _, api, exceptions, fields, models
from odoo.exceptions import AccessError, RedirectWarning, UserError, ValidationError


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move)


        # Si el move_type es del tipo factura de venta
        if move.move_type in ['out_invoice']:

            # Si la factura aun no está aprobada por sifen no se puede revertir
            if move.es_documento_electronico() and move.estado_set != "aprobado":
                raise ValidationError(_("La factura debe estar aprobada por SIFEN para poder hacer una Nota de Crédito."))

            res['tipo_documento'] = "out_refund"
            res['nro_factura_asociada'] = move.id
            fecha = self.env["fe.de"].obtener_hora_actual_set()
            res['invoice_datetime'] = fecha

        return res
