from odoo import api, fields, models, exceptions

class HRNovedadesDesembolsoWizard(models.TransientModel):
    _inherit = 'hr.novedades.desembolso_wizard'
    
    
    def button_create_account_payment(self):
        novedades = self.novedades_ids.filtered(lambda x: x.tipo_id.desembolso and x.state in ['done', 'procesado'] and not x.payment_id)
        for novedad_tipo in novedades.tipo_id:
            novedades_tipo = novedades.filtered(lambda x: x.tipo_id == novedad_tipo)
            lines = []
            total_desembolso = 0
            for novedad in novedades_tipo:
                if not novedad.sudo().contract_id.employee_id.address_home_id:
                    raise exceptions.ValidationError(
                        "El empleado " + novedad.contract_id.employee_id.name + " no tiene asignado un contacto, primero debe de asignarle un contacto antes de poder crear un pago"
                    )
                payment_amount = self.get_novedad_amount(novedad)

                total_desembolso += payment_amount
                lines.append((0, 0, {
                    'partner_id': novedad.contract_id.employee_id.address_home_id.id,
                    'account_id': novedad.tipo_id.account_account_desembolso_id.id,
                    'debit': payment_amount,
                    'name': novedad.employee_id.name,
                }))
            if novedades_tipo and lines:
                tipo_id = novedad_tipo
                if tipo_id.cuentas_pagos_pendientes:
                    manual_method_line = self.account_journal_id.outbound_payment_method_line_ids.filtered(lambda line: line.payment_method_id.name == 'Manual')

                    if manual_method_line and manual_method_line[0].payment_account_id:
                        # Buscar "Cuentas de Pagos Pendientes" en el diario.
                        payment_account_id = manual_method_line[0].payment_account_id.id if manual_method_line[0].payment_account_id else False
                        
                        move_date = max(novedades_tipo.mapped('fecha'))
                        lines.append((0, 0, {
                            'account_id': payment_account_id,
                            'credit': total_desembolso,
                            'name': novedad_tipo.name + ' - ' + str(move_date),
                        }))
                    else :
                        # Si no se encuentra cargado "Cuentas de Pagos Pendientes" en el diario, usar la "Cuenta de pagos pendientes" de contabilidad.
                        company = self.env.company
                        pending_payment_account_id = company.account_journal_payment_credit_account_id.id if company.account_journal_payment_credit_account_id else False

                        if not pending_payment_account_id:
                            raise exceptions.ValidationError("No se ha configurado una 'Cuenta de pagos pendientes' en los ajustes de contabilidad para la compañía.")
                        
                        move_date = max(novedades_tipo.mapped('fecha'))
                        lines.append((0, 0, {
                            'account_id': pending_payment_account_id,
                            'credit': total_desembolso,
                            'name': novedad_tipo.name + ' - ' + str(move_date),
                        }))  
                else: 
                    move_date = max(novedades_tipo.mapped('fecha'))
                    lines.append((0, 0, {
                        'account_id': self.account_journal_id.default_account_id.id,
                        'credit': total_desembolso,
                        'name': novedad_tipo.name + ' - ' + str(move_date),
                    }))  
                    
                payment = self.env['account.move'].sudo().create({
                    'journal_id': self.account_journal_id.id,
                    'date': move_date,
                    'line_ids': lines
                })
                novedades_tipo.sudo().write({'payment_id': payment.id})
                if self.confirm_payment:
                    payment.sudo().action_post()
        