# -*- coding: utf-8 -*-
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    nuevo_estado = fields.Selection([
        ('draft', 'Petición Presupuesto'),
        ('sent', 'Solicitud de presupuesto Enviada'),
        ('to approve', 'Para aprobar'),
        ('purchase', 'Pedido de Compra'),
        ('done', 'Bloqueado'),
        ('cancel', 'Cancelado'),
        ('recepcion_incompleta', 'Recepción incompelta'),
        ('recepcionado', 'Recepcionado'),
        ('facturacion_incompleta', 'Facturación Incompleta'),
        ('finalizado', 'Finalizado')],
        'Estado',
        default='draft', compute="compute_nuevo_estado")

    def compute_nuevo_estado(self):
        for this in self:
            # Toma el estado del state original en caso de que no tome otro estado
            this.nuevo_estado = this.state

            # Si el estado original se encuentra entre estos, se respeta y pasa a la siguiente iteración
            if this.state in ['done', 'cancel', 'sent', 'draft']:
                continue

            this.nuevo_estado_payment_status()

            # Solo obtiene el estado de delivery si es que aún no tiene estado de pago/facturación
            if this.nuevo_estado not in ['facturacion_incompleta', 'finalizado']:
                this.nuevo_estado_delivery_status()

    def nuevo_estado_payment_status(self):
        for this in self:
            invoices = this.invoice_ids.filtered(lambda x: x.state == 'posted')
            payment_states = invoices.mapped('payment_state')
            total_qty_invoiced = sum(this.mapped('order_line.qty_invoiced'))
            total_product_qty = sum(this.mapped('order_line.product_qty'))
            is_fully_invoiced = total_product_qty - total_qty_invoiced <= 0

            if 'in_payment' in payment_states or 'partial' in payment_states:
                this.nuevo_estado = 'facturacion_incompleta'
                continue

            invoices_left_to_pay = [payment_state for payment_state in payment_states if payment_state != 'paid']

            # Si hay alguna factura distinta a pagada y si ya se ha realizado el 100% de las entregas pasa a finalizado
            if 'paid' in payment_states and not invoices_left_to_pay and is_fully_invoiced:
                this.nuevo_estado = 'finalizado'
            elif 'paid' in payment_states and (not is_fully_invoiced or invoices_left_to_pay):
                this.nuevo_estado = 'facturacion_incompleta'

    def nuevo_estado_delivery_status(self):
        for this in self:
            total_delivered = sum(this.mapped('order_line.qty_received'))
            total_product_qty = sum(this.mapped('order_line.product_qty'))
            has_product_lines = len(this.order_line) > 0
            is_fully_delivered = has_product_lines and total_product_qty - total_delivered <= 0

            if is_fully_delivered:
                this.nuevo_estado = 'recepcionado'
            elif not is_fully_delivered and total_delivered > 0:
                this.nuevo_estado = 'recepcion_incompleta'
