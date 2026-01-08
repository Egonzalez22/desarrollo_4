from odoo import models, fields, api


class ReporteRecibo(models.AbstractModel):
    _inherit = 'report.interfaces_payment.reporte_pagos_editado_multi'

    def match_invoice_payments(self, facturas, payments):

        invoice_payments = {}
        
        move_ids = payments.mapped('id')

        for factura in facturas:
            invoice_payments_widget = factura.invoice_payments_widget

            if not invoice_payments_widget or not 'content' in invoice_payments_widget:
                continue

            for payment in invoice_payments_widget['content']:
                if payment.get('is_exchange', False):
                    continue

                if not payment.get('account_payment_id', False) in move_ids:
                    continue
                
                if invoice_payments.get(factura.id, False):
                    invoice_payments[factura.id] += payment['amount']
                else:
                    invoice_payments[factura.id] = payment['amount']

    
        return invoice_payments

    @api.model
    def _get_report_values(self, docids, data=None):
        result = super(ReporteRecibo, self)._get_report_values(docids, data)

        payments = self.env['account.payment'].browse(docids)

        result['pagos'] = {}

        if payments:
            facturas = payments.mapped('reconciled_invoice_ids')

            if facturas:
                result['pagos'] = self.match_invoice_payments(facturas, payments)
                
        return result