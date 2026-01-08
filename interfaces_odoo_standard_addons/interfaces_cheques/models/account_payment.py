from odoo import models, fields, api, exceptions


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    tipo_cheque = fields.Selection(string="Tipo de cheque", selection=[('propio', 'Propio'), ('tercero', 'Tercero')])
    estado_cheque = fields.Selection(string="Estado del cheque", selection=[
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('rechazado', 'Rechazado')
    ], copy=False)
    rechazo_move_id = fields.Many2one('account.move', string='Asiento de rechazo', copy=False)

    def marcar_pagado(self):
        self.write({'estado_cheque': 'pagado'})

    def write(self, vals):
        result = super(AccountPayment, self).write(vals)
        for this in self:
            journal_id = this.journal_actual_id
            if this.estado_cheque != 'pagado' and journal_id and not journal_id.es_diario_tesoreria:
                this.estado_cheque = 'pagado'
        return result

    @api.model
    def create(self, vals):
        result = super().create(vals)
        for this in result:
            if this.tipo_pago == 'Cheque':
                if this.payment_type == 'inbound':
                    this.tipo_cheque = 'tercero'
                elif this.payment_type == 'inbound':
                    this.tipo_cheque = 'propio'
                this.estado_cheque = 'pendiente'
        return result
