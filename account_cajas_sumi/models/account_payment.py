from odoo import api, exceptions, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    def action_draft(self):
        # sumi_addons/accuont_cajas_sumi/models/account_payment.py
        """ 
        Sobreescribimos el action_draft para que se borre el campo en el bank_statement_line_id
        """
        res = super(AccountPayment, self).action_draft()

        for i in self:

            if i.payment_type =='inbound' and not i.is_internal_transfer:
                # Solamente se pueden eliminar registros si la caja está abierta o en proceso de cierre
                if i.caja_session_id and i.caja_session_id.state in ['cierre','proceso']:
                    for st in i.caja_session_id.statement_ids:
                        lines = st.line_ids.filtered(lambda l: l.payment_id == i)
                        if lines:
                            lines.unlink()

                            # Si el diario es de tipo banco, se debe restar el monto del recibo al balance_end_real
                            if i.caja_session_id.state == 'cierre' and st.journal_id.type == 'bank':
                                st.write({'balance_end_real': st.balance_end_real-i.amount})
                else:
                    msg = 'Sólo se puede restablecer a borrador un pago si su sesión de caja está abierta o en proceso de cierre.'
                    raise exceptions.ValidationError(msg)

        return res