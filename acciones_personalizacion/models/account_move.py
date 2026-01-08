from odoo import models, fields, api

from datetime import datetime, timedelta

class AccountMove(models.Model):
    _inherit = 'account.move'
    

    @api.model
    def bloqueo_clientes(self):
        today = fields.Date.today()
        for record in self:
            if record.journal_id.control_bloqueo == True:
                if record.move_type == 'out_invoice' and record.payment_state in ('in_payment', 'not_paid') and record.invoice_payment_term_id.control_bloqueo == True:
                    due_date = record.invoice_date
                    if record.invoice_payment_term_id.control_bloqueo_30_dias == True:
                        extended_due_date = due_date + timedelta(days=60)
                        if today > extended_due_date:
                            record.partner_id.write({'bloqueado': True})
                    else:
                        if today > due_date:
                            record.partner_id.write({'bloqueado': True})



