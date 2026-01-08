from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    numero_recibo_original = fields.Integer(string='Numero de recibo original')


    # def action_post(self):
    #     res = super(AccountPayment, self).action_post()
    #     for payment in self:
    #         # if payment.name and not payment.nro_recibo:
               
    #         #     partes = payment.name.split("/")
    #         #     ultimo_valor = partes[-1]
    #         #     payment.write({'nro_recibo': ultimo_valor})
    #         if not payment.nro_recibo and payment.payment_type == 'inbound':
    #             seq_name = f'seq_rec_cliente'
    #             secuencia = self.env['ir.sequence'].sudo().next_by_code(seq_name)
                

    #             payment.nro_recibo = secuencia
    #             payment.numero_recibo_original = secuencia


    #     return res
    @api.depends('payment_type')
    def genera_secuencia_rp(self):
        if self.payment_type == 'inbound':
            seq_name = f'seq_rec_cliente'
            seq = self.env['ir.sequence'].sudo().next_by_code(seq_name)
            return seq
        return False

    
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for payment in self:
            if not payment.nro_recibo and payment.payment_type == 'inbound':
                # new_recibo_number = payment.genera_secuencia_rp()
                # if not new_recibo_number:
                max_recibo_number = self.env['account.payment'].search([('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),('nro_recibo', '!=', '')], order='id desc', limit=1)
                if max_recibo_number:
                    new_recibo_number = int(max_recibo_number.nro_recibo) + 1
                else:
                    new_recibo_number = 1

                # # Asignar el nuevo número de recibo
                payment.nro_recibo = new_recibo_number
                payment.numero_recibo_original = new_recibo_number


        return res

    @api.model
    def update_nro_recibo(self):
        ##actualizacion de numero de recibo en test
        payments = self.env['account.payment'].search([('payment_type', '=', 'inbound'),
                                                        ('state', '=', 'posted')])
        if payments:
            for pay in payments:
                pay.write({
                            'nro_recibo' : False
                        })