from odoo import fields, api, models, exceptions


class PaymentGroup(models.Model):
    _inherit = "grupo_account_payment.payment.group"

    show_emitir_retencion = fields.Boolean(default=False, compute="_get_show_emitir_retencion", store=True)

    @api.depends("state", "invoice_ids")
    @api.onchange("state", "invoice_ids")
    def _get_show_emitir_retencion(self):
        for this in self:
            show_emitir_retencion = False
            if this.payment_type == "outbound" and this.state == "draft" and this.invoice_ids:
                show_emitir_retencion = True
            this.show_emitir_retencion = show_emitir_retencion

    def action_emitir_retencion(self):
        view_id = self.env.ref("l10n_py_retenciones.emitir_retencion_wizard_view_form")
        return {
            "name": "Emitir retención",
            "view_mode": "form",
            "view_id": view_id.id,
            "res_model": "emitir.retencion.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"default_fecha_retencion": fields.Date.today(), "default_invoice_ids": self.invoice_ids.ids},
        }
