# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models


class InformeOrdenPagoGrupal(models.AbstractModel):
    _name = 'report.orden_pago.orden_pago'

    @api.model
    def _get_report_values(self, docids, data=None):
        ids = data.get('ids', [])
        referencia = data.get('referencia', '')
        ordenes = self.env['orden_pago.orden_pago'].browse(ids)

        data = {
            'company': self.env.company,
            'docs': ordenes,
            'referencia': referencia,
            'currency': self.env.company.currency_id,
        }

        return data