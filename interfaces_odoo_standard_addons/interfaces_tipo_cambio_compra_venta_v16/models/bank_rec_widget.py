from odoo import fields, models, api, exceptions, _, release, Command
from lxml import etree


class BankRecWidget(models.Model):
    _inherit = 'bank.rec.widget'

    automatic_currency_rate_possible = fields.Boolean(related='st_line_id.automatic_currency_rate_possible')

    def _lines_widget_recompute_exchange_diff(self):
        # interfaces_tipo_cambio_compra_venta_v16/models/bank_rec_widget.py
        res = super()._lines_widget_recompute_exchange_diff()

        line_ids_commands = []

        # Clean the existing lines.
        for exchange_diff in self.line_ids.filtered(lambda x: x.flag == 'exchange_diff'):
            line_ids_commands.append(Command.unlink(exchange_diff.id))

        new_amls = self.line_ids.filtered(lambda x: x.flag == 'new_aml')
        for new_aml in new_amls:

            # Compute the balance of the line using the rate/currency coming from the bank transaction.
            amounts_in_st_curr = self.st_line_id._prepare_counterpart_amounts_using_st_line_rate(
                new_aml.currency_id,
                new_aml.balance,
                new_aml.amount_currency,
            )
            balance = amounts_in_st_curr['balance']
            if new_aml.currency_id == self.company_currency_id and self.transaction_currency_id != self.company_currency_id:
                # The reconciliation will be expressed using the rate of the statement line.
                balance = new_aml.balance
            elif new_aml.currency_id != self.company_currency_id and self.transaction_currency_id == self.company_currency_id:
                # The reconciliation will be expressed using the foreign currency of the aml to cover the Mexican
                # case.
                balance = new_aml.currency_id._convert_tipo_cambio_vendedor(
                    new_aml.amount_currency,
                    self.transaction_currency_id,
                    self.company_id,
                    self.st_line_id.date,
                    force_rate=self.st_line_id.currency_rate
                )

            # Compute the exchange difference balance.
            exchange_diff_balance = balance - new_aml.balance
            if self.company_currency_id.is_zero(exchange_diff_balance):
                continue

            expense_exchange_account = self.company_id.expense_currency_exchange_account_id
            income_exchange_account = self.company_id.income_currency_exchange_account_id

            if exchange_diff_balance > 0.0:
                account = expense_exchange_account
            else:
                account = income_exchange_account

            line_ids_commands.append(Command.create({
                'flag': 'exchange_diff',
                'source_aml_id': new_aml.source_aml_id.id,

                'account_id': account.id,
                'date': new_aml.date,
                'name': _("Exchange Difference: %s", new_aml.name),
                'partner_id': new_aml.partner_id.id,
                'currency_id': new_aml.currency_id.id,
                'amount_currency': exchange_diff_balance if new_aml.currency_id == self.company_currency_id else 0.0,
                'balance': exchange_diff_balance,
            }))

        if line_ids_commands:
            self.line_ids = line_ids_commands
            # Reorder to put each exchange line right after the corresponding new_aml.
            new_lines = self.env['bank.rec.widget.line']
            for line in self.line_ids:
                if line.flag == 'exchange_diff':
                    continue

                new_lines |= line
                if line.flag == 'new_aml':
                    exchange_diff = self.line_ids \
                        .filtered(lambda x: x.flag == 'exchange_diff' and x.source_aml_id == line.source_aml_id)
                    new_lines |= exchange_diff
            self.line_ids = new_lines
        return res

    def button_validate(self, async_action=False):
        for this in self:
            if this.st_line_id.compute_currency_rate_for_line and not this.st_line_id.freeze_currency_rate and this.st_line_id.currency_id != this.st_line_id.company_id.currency_id:
                if len(this.line_ids.source_aml_id.currency_id) != 1:
                    continue
                lines_to_process = this.line_ids.filtered(lambda x: x.flag == 'new_aml')
                amls = lines_to_process.source_aml_id
                total_amount_currency = sum(abs(line.source_aml_id.amount_currency) for line in lines_to_process)
                total_amount = sum(abs(line.source_aml_id.balance) for line in lines_to_process)
                lines_to_process.unlink()
                this.st_line_id.freeze_currency_rate = True
                if not total_amount_currency: total_amount_currency = 1
                this.st_line_id.currency_rate = total_amount / total_amount_currency
                this._action_add_new_amls(amls)
        result = super(BankRecWidget, self).button_validate(async_action)
        return result
