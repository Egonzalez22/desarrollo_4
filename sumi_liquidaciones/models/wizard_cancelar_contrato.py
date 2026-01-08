from odoo import models, fields, api


class CancelContractWizard(models.TransientModel):
    _name = "hr.contract.cancel.wizard"
    _description = "Wizard para Cancelar Contrato"

    motivo_salida_id = fields.Many2one(
        "sumi_liquidaciones.motivo_salida", string="Motivo de salida", required=True
    )

    contract_id = fields.Many2one("hr.contract", string="Contrato", required=True)

    def confirm_cancel(self):
        self.contract_id.with_context(from_cancel_wizard=True).write(
            {
                "motivo_salida_id": self.motivo_salida_id.id,
                "state": "cancel",
            }
        )

    def confirm_close(self):
        self.contract_id.with_context(from_cancel_wizard=True).write(
            {
                "motivo_salida_id": self.motivo_salida_id.id,
                "state": "close",
            }
        )
