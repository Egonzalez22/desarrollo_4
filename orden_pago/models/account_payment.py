from odoo import api, exceptions, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    orden_pago_id = fields.Many2one('orden_pago.orden_pago', string="Orden de Pago")

    # def action_post(self):
    #     requiere_op=self.env.company.requiere_op
    #     for i in self:
    #         if requiere_op and i.payment_type=='outbound' and not i.is_internal_transfer and not i.solicitud_pago_id:
    #             raise exceptions.ValidationError('No se puede crear un pago sin una Orden de pago confirmada')
    #     return super(AccountPayment,self).action_post()

    # @api.model
    # def create(self,vals):
    #     res=super(AccountPayment,self).create(vals)
    #     if vals.get('solicitud_pago_id') and res:
    #         solicitud_id=self.env['agrinvest_solicitud_pago.solicitud_pago'].browse(vals.get('solicitud_pago_id'))
    #         solicitud_id.write({'payment_id':res.id})
    #     return res
    # def write(self,vals):
    #     res=super(AccountPayment,self).write(vals)
    #     if vals.get('solicitud_pago_id') and res:
    #         solicitud_id=self.env['agrinvest_solicitud_pago.solicitud_pago'].browse(vals.get('solicitud_pago_id'))
    #         solicitud_id.write({'payment_id':res.id})
    #     return res
