from odoo import api, fields, models, exceptions


class account_payment(models.Model):
    _inherit = 'account.payment'

    caja_session_id = fields.Many2one(
        'account.caja.session', string="Sesión de caja", copy=False)

    def get_sesion(self):
        # account_cajas/models/account_payment.py
        sesion = self.env['account.caja.session'].search([
            ('company_id', '=', self.company_id.id or self.env.company.id),
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'proceso')
        ])
        return sesion
    
    def comprobar_sesion_caja(self):
        for this in self:
            # Si en el contexto viene "excluir_control_cajas", retornamos False directamente para que no se compruebe. (Se puede usar para pagos desde el ecommerce)
            if self.env.context.get('excluir_control_cajas'):
                return False

            if (
                    this.company_id.use_caja_sessions and
                    (
                            this.payment_type == 'inbound' and this.company_id.caja_sessions_inbound_control or
                            this.payment_type == 'outbound' and this.company_id.caja_sessions_outbound_control
                    ) and
                    not this.is_internal_transfer
            ):
                session = this.get_sesion()
                if not this.caja_session_id:
                    if session:
                        this.caja_session_id = session
                        return True
                        
                    else:
                        if not this.journal_id.excluir_sesion:
                            raise exceptions.ValidationError(
                                'No existe ninguna sesión de caja abierta para el usuario %s. Antes debe abrir una.' % (this.env.user.name)
                            )
                else:
                    return True

    def action_post(self):
        # account_cajas/models/account_payment.py
        res = super(account_payment, self).action_post()
        if self.comprobar_sesion_caja():
            for this in self:
                if this.company_id.caja_sessions_inbound_control and this.payment_type == 'inbound' and not this.is_internal_transfer:
                    caja = this.get_sesion().caja_id
                    if this.journal_id.id not in caja.journal_ids.ids:
                        if not this.journal_id.excluir_sesion:
                            raise exceptions.ValidationError(
                                'No se puede crear una linea de pago en el diario %s, el mismo no está habilitado para ésta caja.' % this.journal_id.name)

                # Si la key procesar_statement no existe o es False, entonces se procesa lo relacionado al statement
                if not self.env.context.get('procesar_statement'):
                    if (
                            this.company_id.use_caja_sessions and
                            (
                                    this.payment_type == 'inbound' and this.company_id.caja_sessions_inbound_control or
                                    this.payment_type == 'outbound' and this.company_id.caja_sessions_outbound_control
                            ) and
                            this.state == 'posted' and
                            not this.is_internal_transfer
                    ):
                        sesion = this.get_sesion()
                        for s in sesion.statement_ids.filtered(lambda x: x.aux_journal_id == this.journal_id):
                            monto = this.amount
                            if this.payment_type == 'outbound':
                                monto = monto * -1
                            value = {
                                'date': fields.Date.today(),
                                'partner_id': this.partner_id.id,
                                'amount': monto,
                                'payment_id': this.id,
                                'journal_id': this.journal_id.id,
                                'statement_id': s.id,
                                'payment_ref': this.name
                            }
                            # No debe crear mas TODO
                            line_ids = this.env['account.bank.statement.line'].create(value)
                            s.write({'line_ids': [(4, line_ids.id, 0)]})
        return res

   

    @api.model
    def create(self, vals_list):
        # account_cajas/models/account_payment.py
        result = super(account_payment, self).create(vals_list)
        # result.comprobar_sesion_caja()
        return result

    def action_cancel(self):
        # account_cajas/models/account_payment.py
        res = super(account_payment, self).action_cancel()
        for this in self:
            # Si la key procesar_statement no existe o es False, entonces se procesa lo relacionado al statement
            if (
                    this.company_id.use_caja_sessions and
                    (
                            this.payment_type == 'inbound' and this.company_id.caja_sessions_inbound_control or
                            this.payment_type == 'outbound' and this.company_id.caja_sessions_outbound_control
                    ) and
                    not self.env.context.get('procesar_statement') and
                    not this.is_internal_transfer
            ):
                if this.caja_session_id and this.caja_session_id.state in ['cierre', 'proceso']:
                    res = super(account_payment, this).action_cancel()
                    for st in this.caja_session_id.statement_ids:
                        lines = st.line_ids.filtered(lambda l: l.payment_id == this)
                        if lines:
                            lines.unlink()
                            if this.caja_session_id.state == 'cierre' and st.journal_id.type == 'bank':
                                st.write({'balance_end_real': st.balance_end_real - this.amount})
                else:
                    raise exceptions.ValidationError(
                        'Sólo se puede cancelar un recibo si su sesión de caja está abierta o en proceso de cierre.')
        return res
