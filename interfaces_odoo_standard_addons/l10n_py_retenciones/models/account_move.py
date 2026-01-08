from odoo import _, api, fields, models, exceptions


class AccountMove(models.Model):
    _inherit = "account.move"

    retencion_sugerida = fields.Boolean(string="Retencion sugerida", compute="compute_retencion_sugerida")

    def compute_retencion_sugerida(self):
        for this in self:
            retencion_sugerida = False
            monto_minimo = float(this.env["ir.config_parameter"].sudo().get_param("ret_monto_minimo"))
            if (
                this.move_type == "in_invoice"
                and this.state == "posted"
                and this.company_id.es_agente_retencion
                and abs(this.amount_total_signed) > monto_minimo
                and not this.partner_id.no_retener_iva
            ):
                retencion_sugerida = True
            this.retencion_sugerida = retencion_sugerida

    def action_emitir_retencion(self):
        view_id = self.env.ref("l10n_py_retenciones.emitir_retencion_wizard_view_form")
        default_invoice_ids = self.filtered(lambda x: x.retencion_sugerida)
        if not default_invoice_ids:
            raise exceptions.UserError(
                "No puede ser emitida una retención para ninguna de las facturas seleccionadas, compruebe éstos puntos:\n"
                "- La compañía de la factura debe estar configurada como Agente de Retención.\n"
                "- El monto mínimo de retenciones está definido y la factura debe alcanzar ese monto.\n"
                '- El contacto asociado a la factura no debe tener activada la opción de "No retener IVA".'
            )
        return {
            "name": "Emitir retención",
            "view_mode": "form",
            "view_id": view_id.id,
            "res_model": "emitir.retencion.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"default_fecha_retencion": fields.Date.today(), "default_invoice_ids": default_invoice_ids.ids},
        }
