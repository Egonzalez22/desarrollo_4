from odoo import _, api, fields, models

import json,logging,requests
_logger=logging.getLogger("WhatsApp API")

class InterfacesWhatsappApiMessage(models.Model):
    _name = 'interfaces_whatsapp_api.message'
    _description = 'Mensaje de WhatsApp'
    _order='id desc'

    name = fields.Char(string="ID del mensaje")
    company_id = fields.Many2one(
        'res.company', string="Compañía", default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="Contacto")
    template_id = fields.Many2one(
        'interfaces_whatsapp_api.message.template', string="Plantilla de mensaje")
    direccion_mensaje=fields.Selection(string="Sentido del mensaje",selection=[('inbound','Entrante'),('outbound','Saliente')])
    message_type = fields.Selection(string="Tipo de mensaje", selection=[
                                    ('template', 'Plantilla'),('text','Texto')], default='text')
    message_text = fields.Text(string="Texto del mensaje")
    status_code=fields.Char(string="Status code",copy=False)
    response_id=fields.Char(string="ID de respuesta de API",copy=False)
    response_text=fields.Char(string="Texto de respuesta de API",copy=False)
    state=fields.Selection(string="Estado",selection=[('draft','Borrador'),('sent','Enviado')],default='draft',copy=False)
    from_number=fields.Char(string="Nro. remitente",copy=False)
    from_name=fields.Char(string="Nombre del remitente",copy=False)


    def button_enviar_mensaje(self):
        for i in self:
            i.action_send_message(i.partner_id.phone,i.message_type,i.message_text,i.template_id.name or False)

    @api.model
    def action_send_message(self, to_number, message_type='template', message_text=False, template_name='hello_world', template_lang='en_US'):
        try:
            version = self.env.company.wha_version
            phone_number_id = self.env.company.wha_phone_number_id
            url = "https://graph.facebook.com/%s/%s/messages" % (
                version, phone_number_id)
            token = self.env.company.wha_user_access_token
            headers = {
                'Authorization': 'Bearer %s' % token,
                'Content-Type': 'application/json'
            }
            data = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': message_type,
                'text':{
                    'body':message_text
                },
                'template': {
                    'name': template_name,
                    'language': {
                        'code': template_lang
                    }
                }

            }
            res=requests.post(url=url, headers=headers, data=json.dumps(data))
            
            res_json=res.json()
            if self:
                vals={'status_code':res.status_code,'response_text':res.text,'direccion_mensaje':'outbound','state':'sent'}
                if res_json.get("messages") and res_json.get("messages")[0] and res_json.get("messages")[0].get("id"):
                    response_id=res_json.get("messages")[0].get("id")
                    if response_id:
                        vals['response_id']=response_id

                self.write(vals)
            _logger.info("Respuesta de API de WhatsApp: %s"%res.text)
        except Exception as ex:
            _logger.error("Respuesta de API de WhatsApp: %s"%ex)

    @api.model
    def create(self,vals):
        res=super(InterfacesWhatsappApiMessage,self).create(vals)
        if res:
            res.write({'name':'MSG %s'%str(res.id)})
        return res
