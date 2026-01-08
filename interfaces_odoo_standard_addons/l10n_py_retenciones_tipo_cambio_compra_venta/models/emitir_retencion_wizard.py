# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmitirRetencionWizard(models.TransientModel):
    _inherit = "emitir.retencion.wizard"

    def create_payment_values(self, record):
        # l10n_py_retenciones_tipo_cambio_compra_venta/models/models.py
        payment_values = super(EmitirRetencionWizard, self).create_payment_values(record)
        if record.move_id.freeze_currency_rate:
            payment_values["currency_rate"] = record.move_id.currency_rate
            payment_values["freeze_currency_rate"] = record.move_id.freeze_currency_rate
        return payment_values
