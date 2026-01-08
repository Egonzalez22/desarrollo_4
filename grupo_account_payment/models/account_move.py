from odoo import fields, api, models, exceptions
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_pago(self):
        if self.type == 'out_invoice':
            flag = self.env.user.has_group(
                'grupo_account_payment.grupo_cobrador')
            if flag:
                view = self.env.ref(
                    'grupo_account_payment.grupo_account_payment_form_view')
                return {
                    'name': 'Registrar pago',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'grupo_account_payment.payment.group',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    # 'target': 'new',
                    'context': {'default_payment_type': 'inbound', 'default_partner_id': self.partner_id.id, 'default_invoice_ids': self.ids},
                }
            else:
                raise UserError(
                    'Su usuario no cuenta con permisos para registrar pagos')
        elif self.type == 'in_invoice':
            flag = self.env['res.users'].has_group(
                'grupo_account_payment.grupo_orden_pago')
            if flag:
                view = self.env.ref(
                    'grupo_account_payment.grupo_account_payment_orden_form_view')
                return {
                    'name': 'Registrar pago',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'grupo_account_payment.payment.group',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    # 'target': 'new',
                    'context': {'default_payment_type': 'outbound', 'default_partner_id': self.partner_id.id, 'default_invoice_ids': [(4, self.id, 0)]},
                }
            else:
                raise UserError(
                    'Su usuario no cuenta con permisos para registrar órdenes de pago')

    @api.model
    def button_pago_multi(self, facturas):
        if facturas[0].type == 'out_invoice':
            flag = self.env.user.has_group(
                'grupo_account_payment.grupo_cobrador')
            if flag:
                view = self.env.ref(
                    'grupo_account_payment.grupo_account_payment_form_view')
                return {
                    'name': 'Registrar pago',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'grupo_account_payment.payment.group',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    # 'target': 'new',
                    'context': {'default_payment_type': 'inbound', 'default_partner_id': facturas[0].partner_id.id, 'default_invoice_ids': [(6, 0, facturas.ids)]},
                }
            else:
                raise UserError(
                    'Su usuario no cuenta con permisos para registrar pagos')

        elif facturas[0].type == 'in_invoice':
            flag = self.env.user.has_group(
                'grupo_account_payment.grupo_orden_pago')
            if flag:
                view = self.env.ref(
                    'grupo_account_payment.grupo_account_payment_orden_form_view')
                return {
                    'name': 'Registrar pago',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'grupo_account_payment.payment.group',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    # 'target': 'new',
                    'context': {'default_payment_type': 'outbound', 'default_partner_id': self.partner_id.id, 'default_invoice_ids': [(6, 0, facturas.ids)]},
                }
            else:
                raise UserError(
                    'Su usuario no cuenta con permisos para registrar ordenes de pago')
                
                

    def action_register_payment(self):
        if not self.ids:
            raise UserError("No se seleccionaron facturas.")
    
        partner_ids = self.mapped('partner_id')
        while True :
            break_loop = True
            for partner_id in partner_ids :
                if partner_id.parent_id and not partner_id.parent_id  in partner_ids :
                    partner_ids |= partner_id.parent_id
                    break_loop = False
            if break_loop :
                break    
        
        partner_ids = partner_ids.filtered(lambda x:not x.parent_id)
        
        if len(partner_ids) > 1:
            raise UserError("No puede seleccionar facturas de diferentes clientes.")
        
        invalid_state_invoices = self.filtered(lambda inv: inv.payment_state not in ('not_paid', 'partial'))
        if invalid_state_invoices:
            raise UserError("Solo se pueden seleccionar facturas no pagadas o parcialmente pagadas.")
        
        invalid_state = self.filtered(lambda inv: inv.state not in ('posted'))
        if invalid_state:
            raise UserError("Solo se pueden seleccionar facturas en estado publicado.")
        
        move_type = list(set(self.mapped('move_type')))        
        
        if len(move_type) > 1 :
             raise UserError("Todas las facturas seleccionadas deben ser del mismo tipo.")
        
        move_type = move_type[0]
        
        context = {
            'default_payment_type': 'inbound' if move_type == 'out_invoice' else 'outbound',
            'default_partner_type': 'customer' if move_type == 'out_invoice' else 'supplier',
            'default_partner_id': partner_ids.id,
            # 'default_invoice_ids': [(6, 0, self.ids)],
            'default_invoice_ids': self.ids,
            'default_currency_id': self[0].currency_id.id,
            'default_move_journal_types': ('bank', 'cash'),
            'search_default_company_id': self.env.user.company_id.id,
            'search_default_child_of_company_id': [self.env.user.company_id.id] + [child.id for child in self.env.user.company_id.child_ids],
        }
        if self[0].move_type == 'out_invoice':
            context["search_default_inbound_filter"] = 1
        elif self[0].move_type == 'in_invoice':
            context["search_default_outbound_filter"] = 1

        view_id = self.env.ref('grupo_account_payment.account_payment_form_view').id
        action = {
                'name': 'Registrar Pago',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'grupo_account_payment.payment.group',
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new',
            }

        return action   