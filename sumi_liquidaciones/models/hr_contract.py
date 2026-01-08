# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import UserError


class HrContract(models.Model):
    _inherit = "hr.contract"

    motivo_salida_id = fields.Many2one(
        "sumi_liquidaciones.motivo_salida", string="Motivo de salida"
    )

    def action_cancel_contract_wizard(self):
        return {
            "name": "Cancelar Contrato",
            "type": "ir.actions.act_window",
            "res_model": "hr.contract.cancel.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_contract_id": self.id,
            },
        }

    def write(self, vals):
        # Validación para evitar cambios manuales a cancel o close
        if "state" in vals and vals["state"] in ("cancel", "close"):
            if not self.env.context.get("from_cancel_wizard"):
                raise UserError(
                    "No se puede cambiar el estado a 'Vencido' o 'Cancelado' directamente. Use el botón 'Dar de baja Contrato'."
                )

        # Si cambia a draft o open, limpiar el motivo de salida
        if "state" in vals and vals["state"] in ("draft", "open"):
            vals["motivo_salida_id"] = False

        return super().write(vals)
