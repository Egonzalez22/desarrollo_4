from odoo import api, fields, models
import json

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    monto_letras = fields.Char(string='Monto en letras', compute="compute_monto_letras", store=True, copy=False)

    @api.onchange('amount_total')
    @api.depends('amount_total')
    def compute_monto_letras(self):
        for i in self:
            if i.amount_total:
                i.monto_letras = self.amount_to_text(i.amount_total, None)

    
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = self.env['interfaces_tools.tools'].numero_a_letra(amount)
        return convert_amount_in_words

    def format_monto(self,monto):
        return self.env['interfaces_tools.tools'].format_amount(monto,currency=self.currency_id)
    
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        if self.move_type == 'out_invoice':
            self.ensure_one()
            self.sent = True
            return self.env.ref('interfaces_facturas.facturas_interfaces').report_action(self)