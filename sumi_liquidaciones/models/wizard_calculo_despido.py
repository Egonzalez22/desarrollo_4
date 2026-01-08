# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import fields, api, models, _


class WizardCalculoDespido(models.TransientModel):
    _inherit = "wizard.calculo.despido"

    motivo_salida_id = fields.Many2one(
        "sumi_liquidaciones.motivo_salida", string="Motivo de salida"
    )
    

    def let_the_purge_begin(self):
        # Llama a la función original
        result = super(WizardCalculoDespido, self).let_the_purge_begin()
        if isinstance(result, dict) and result.get("res_id"):
            payslip_id = result["res_id"]
            payslip = self.env["hr.payslip"].browse(payslip_id)
            if payslip:
                if self.motivo_salida_id:
                    payslip.write({
                        "motivo_salida_id": self.motivo_salida_id.id,
                    })

                    if self.contract_id:
                        self.contract_id.write({
                            "motivo_salida_id": self.motivo_salida_id.id,
                        })

        return result