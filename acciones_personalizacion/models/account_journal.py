from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    transferencia_automatica = fields.Boolean(string='Transferencia automatica')
    cuenta_transferencia_automatica = fields.Many2one('account.account', string='Cuenta de transferencia automatica')
    control_bloqueo = fields.Boolean(string='Control para bloqueo')


    def control_asiento(self):
        diarios = self.env['account.journal'].search([
            ('transferencia_automatica','=', 'True'), ('cuenta_transferencia_automatica','!=', ''),
            ])

        for diario in diarios:
            
            move_line = self.env['account.move.line'].search([
            ('account_id','=', diario.default_account_id.id)
            ])
            for line in move_line:
                
                fecha_actual = fields.Date.context_today(self)
                if line.debit:
                    move_obj = self.env['account.move']
                    nuevo_asiento = move_obj.create({
                        'ref': 'Transferencia automática', 
                        'date': fecha_actual,
                    })
                    line_obj = self.env['account.move.line']
                    nueva_linea = line_obj.create({
                        'move_id': nuevo_asiento.id, 
                        'account_id': diario.cuenta_transferencia_automatica.id,
                        'partner_id': line.partner_id.id,  
                        'name': 'Cuenta de origen se acredita',
                        'credit':line.debit
                    })
                    todo_listo = True  

                    if todo_listo:
                        nuevo_asiento.post()

                    

                if line.credit:
                    move_obj = self.env['account.move']
                    nuevo_asiento = move_obj.create({
                        'ref': 'Transferencia automática', 
                        'date': fecha_actual,
                    })
                    line_obj = self.env['account.move.line']
                    nueva_linea = line_obj.create({
                        'move_id': nuevo_asiento.id, 
                        'account_id': diario.cuenta_transferencia_automatica.id,
                        'partner_id': line.partner_id.id,  
                        'name': 'Cuenta de origen se debita',
                        'debit':line.credit
                    })
                    todo_listo = True  

                    if todo_listo:
                        nuevo_asiento.post()



       