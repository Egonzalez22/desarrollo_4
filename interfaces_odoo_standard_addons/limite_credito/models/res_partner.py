from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Campos para el limite de credito de zumi
    credito_aprobado = fields.Boolean(string='Crédito aprobado', default=False)

    # Agregamos checks para permitir superar limite de credito y para bloquear un cliente
    puede_superar_credito = fields.Boolean(string='Puede superar limite de crédito', default=False)
    bloqueado = fields.Boolean(string='Bloqueado', default=False)
    motivo_bloqueo = fields.Char(string='Motivo de bloqueo')
    puede_generar_fact_contado = fields.Boolean(string='Puede generar factura contado', default=True)

    # Totales
    total_nc = fields.Monetary(string='Total nota de crédito', default=0.0)
    total_pagos_sin_factura = fields.Monetary(string='Total pagos sin factura', default=0.0)
    total_cheques_diferidos = fields.Monetary(string='Total cheques diferidos', default=0.0)

    credito_disponible = fields.Float(string='Crédito disponible', compute='_compute_credito_disponible')

    # Campos relacionados con las referencias
    ref_banc_banco = fields.Char(string='Banco')
    ref_banc_agencia = fields.Char(string='Agencia')
    ref_banc_telefono = fields.Char(string='Teléfono')
    ref_banc_agente = fields.Char(string='Agente Bancario')

    ref_com_nombre = fields.Char(string='Razón Social o Nombre')
    ref_com_telefono = fields.Char(string='Teléfono')

    # Calculamos el credito disponible de un cliente
    def _compute_credito_disponible(self):
        for partner in self:
            # 1 -  Notas de credito del cliente
            nc_domain = [
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_refund'),
                ('state', '=', 'posted'),
            ]
            nc_invoices = self.env["account.move"].search(nc_domain).mapped('amount_total')

            # 2 - Cheques diferidos, la fecha_vencimiento_cheque es > a la fecha_cheque
            checks_domain = [
                ('partner_id', '=', partner.id),
                ('tipo_pago', '=', 'Cheque'),
                ('payment_type', '=', 'inbound'),
                ('es_diferido', '=', True),
                ('is_reconciled', '=', False),
                ('is_matched', '=', True),
            ]
            checks_invoices = self.env["account.payment"].search(checks_domain).mapped('amount')

            # 3 - Todos los pagos del cliente, que no sean del tipo cheque y no tenga una factura asociada
            payments_domain = [
                ('partner_id', '=', partner.id),
                ('tipo_pago', '!=', 'Cheque'),
                ('state', '=', 'posted'),
                ('payment_type', '=', 'inbound'),
                ('is_reconciled', '=', False),
            ]
            payments_invoices = self.env["account.payment"].search(payments_domain).mapped('amount')

            # Obtenemos las sumas
            nc_sum = sum(nc_invoices)
            checks_sum = sum(checks_invoices)
            payments_sum = sum(payments_invoices)

            partner.total_nc = nc_sum
            partner.total_cheques_diferidos = checks_sum
            partner.total_pagos_sin_factura = payments_sum

            disponible = partner.credit_limit - (partner.credit + checks_sum + payments_sum)
            partner.credito_disponible = disponible
