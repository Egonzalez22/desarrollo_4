from odoo import fields, models

class PaymentGroupAccountMove(models.Model):
    _name = 'grupo_account_am'
    _description = 'Histórico de Facturas del Grupo de Pago'

    # Factura asociada
    account_move_id = fields.Many2one('account.move', string="Factura", copy=False, required=True)
    identifier = fields.Integer(related='account_move_id.id', string="ID", store=True, readonly=True)
    name = fields.Char(related='account_move_id.name', string="Número", store=True, readonly=True)
    invoice_date = fields.Date(related='account_move_id.invoice_date', string="Fecha de Factura", store=True, readonly=True)
    invoice_date_due = fields.Date(related='account_move_id.invoice_date_due', string="Fecha de Vencimiento", store=True, readonly=True)
    invoice_origin = fields.Char(related='account_move_id.invoice_origin', string="Origen", store=True, readonly=True)
    currency_id = fields.Many2one(related='account_move_id.currency_id', store=True, readonly=True)
    amount_total = fields.Monetary(related='account_move_id.amount_total', string="Total", store=True, readonly=True)
    amount_residual = fields.Monetary(related='account_move_id.amount_residual', string="Saldo Actual", store=True, readonly=True)

    # Campos personalizados
    amount_residual_history = fields.Float(string="Saldo Histórico", help="Saldo de la factura al momento de incluirla en el grupo")
    payment_amount_repartition = fields.Float(string="Monto a Pagar", default=0, help="Monto del pago asignado a esta factura")

    # Relación con el grupo de pago
    payment_group_id = fields.Many2one('grupo_account_payment.payment.group', string="Grupo de Pago", ondelete='cascade', required=True)
