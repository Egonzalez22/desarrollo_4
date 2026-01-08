from odoo import fields, api, models, exceptions


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    

    payment_group_id = fields.Many2one(
        'grupo_account_payment.payment.group', string="Grupo de pago")
 

    @api.constrains('nro_cheque')
    def valida_cheque_duplicado(self):
        if self.nro_cheque:
            duplicado = self.env['account.payment'].search([(
                'bank_id', '=', self.bank_id.id), ('nro_cheque', '=', self.nro_cheque), ('id', '!=', self.id)])
            if duplicado:
                raise exceptions.ValidationError('Cheque ya existente: '+self.bank_id.name+" "+self.nro_cheque)
        else:
            return

    @api.depends('payment_group_id')
    def action_post(self):
        
        if not self.payment_group_id and not self.is_internal_transfer  and not self._context.get('avoid_payment_group'):
            raise exceptions.ValidationError('No puede crear una linea de pago directamente, por favor vaya a Recibos u Ordenes de Pago.')
   
        #if self.payment_group_id and self.currency_id != self.payment_group_id.currency_id :
                
        #    raise exceptions.ValidationError('No se permite la moneda %s para este pago' %self.currency_id.name)
            
        return super(AccountPayment,self).action_post()
    
    
