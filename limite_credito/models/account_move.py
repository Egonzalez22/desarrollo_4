from odoo import _, api, exceptions, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for record in self:
            if record.move_type in ['out_invoice', 'in_invoice']:
                # Si la factura es de contado, y el partner puede generar factura contado, no hacemos nada
                es_contado = record.invoice_date == record.invoice_date_due
                if es_contado and record.partner_id.puede_generar_fact_contado:
                    continue

                # Si el partner esta bloqueado no permitimos que se genere la factura, aun si tiene credito
                if record.partner_id.bloqueado:
                    motivo = record.partner_id.motivo_bloqueo or 'No se especifico motivo'
                    raise exceptions.ValidationError(_(f'El cliente esta bloqueado: {motivo}'))

                # Si el partner no puede superar su limite de credito, prevenimos que se genere la factura
                if not record.partner_id.puede_superar_credito:
                    total_factura = record.amount_total
                    # Verificamos si el total de la factura supera el limite de credito del cliente
                    if total_factura > record.partner_id.credito_disponible:
                        raise exceptions.ValidationError(_('El total de la factura supera el crédito disponible del cliente'))

        return res
