from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    whatsapp_message_ids = fields.One2many(
        'interfaces_whatsapp_api.message', 'partner_id', string="Mensajes de WhatsApp")
    whatsapp_message_count = fields.Integer(
        string="Cant. mensajes", compute="compute_whatsapp_message_count")

    @api.depends('whatsapp_message_ids')
    def compute_whatsapp_message_count(self):
        for i in self:
            i.whatsapp_message_count = len(i.whatsapp_message_ids)

    def action_view_messages(self):
        view_id=self.env.ref('interfaces_whatsapp_api.message_view_tree')
        return {
            'name': 'Mensajes de Whatsapp',
            'view_mode':"tree,form",
            #'view_id': view_id.id,
            'res_model': 'interfaces_whatsapp_api.message',
            'type': 'ir.actions.act_window',
            'context': {'default_partner_id':self.id},
            'domain':[('partner_id','=',self.id)]
        }
