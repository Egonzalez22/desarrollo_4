from odoo import fields, models, api, exceptions, _, release
from lxml import etree


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    automatic_currency_rate_possible = fields.Boolean(compute='_get_automatic_currency_rate_possible', store=False)

    def _get_automatic_currency_rate_possible(self):
        for this in self:
            automatic_currency_rate_possible = False
            if not this.freeze_currency_rate and this.currency_id != this.company_id.currency_id:
                automatic_currency_rate_possible = True
            this.automatic_currency_rate_possible = automatic_currency_rate_possible
