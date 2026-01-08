from odoo import fields,models,api,exceptions


class AccountBankStatement(models.Model):
    _inherit='account.bank.statement'

    aux_journal_id=fields.Many2one('account.journal',copy=False)
    transacciones = fields.Monetary(
        string='Transacciones', compute="compute_transacciones")
    
    @api.depends('line_ids','line_ids.amount')
    def compute_transacciones(self):
        for i in self:
            transacciones=0
            for l in i.line_ids:
                transacciones=transacciones + l.amount
            i.transacciones=transacciones

class AccountBankStatementLine(models.Model):
    _inherit='account.bank.statement.line'

    payment_id=fields.Many2one('account.payment')