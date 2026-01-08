# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models


class WizardInformeOrdenPagoGrupal(models.TransientModel):
    _name = 'orden_pago.orden_pago_informe_wizard'

    referencia = fields.Char("Referencia", required=True)

    def generar_informe(self):
        data = {
            'ids': self.env.context.get('default_ids', []),
            'referencia': self.referencia,
        }

        # Le agregamos el name a todas las ordenes de pago
        ordenes = self.env['orden_pago.orden_pago'].browse(data['ids'])
        for orden in ordenes:
            orden.reporte_name = self.referencia

        report = self.env.ref('orden_pago.orden_pago_action').report_action(self, data=data)
        return report
        # Cerramos el wizard
        # return {'type': 'ir.actions.act_window_close'}

