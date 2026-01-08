# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class AccountCajaSession(models.Model):
    _inherit = 'account.caja.session'

    def button_validar(self):
        if self.env.user == self.user_id or self.env.user.has_group('base.group_system'):
            # for i in self.statement_ids:
            #     # i.button_post()
            #     for j in i.line_ids:
            #         for x in j.payment_id.move_id.line_ids.filtered(lambda z: z.debit > 0 and not z.reconciled):
            #             if j.journal_id.type != 'bank':
            #                 line_to_change = j.line_ids.filtered(lambda x: x.credit > 0 and not x.reconciled)
            #                 line_to_change.write({'account_id': x.account_id.id})
            #                 (x + line_to_change).reconcile()
            #     # i.button_validate_or_action()
            self.write({'state': 'done'})
            return
        else:
            raise exceptions.ValidationError(
                'La sesión está asignada a otro usuario')
