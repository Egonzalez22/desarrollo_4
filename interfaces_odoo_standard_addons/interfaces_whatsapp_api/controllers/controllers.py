# -*- coding: utf-8 -*-
from odoo import http
import json
import logging

_logger = logging.getLogger(__name__)


class InterfacesWhatsappApi(http.Controller):


    def process_messages(self,message,contacts=False):
        
        partner_id=None
        if message.get("context"):
            id_hilo=message.get('context').get('id')
            if id_hilo:
                existing_messages=http.request.env['interfaces_whatsapp_api.message'].sudo().search([('response_id','=',id_hilo)])
                if existing_messages:
                    partner_id=existing_messages[0].partner_id
        if not partner_id and contacts:
            _logger.info(contacts)
            partner_id=http.request.env['res.partner'].sudo().search([('phone','=',contacts[0].get("wa_id"))])
        http.request.env['interfaces_whatsapp_api.message'].sudo().create(
            {
                'message_type':'text',
                'message_text':message.get('text').get('body'),
                'response_id':message.get('context').get('id') if message.get("context") else False,
                'direccion_mensaje':'inbound',
                'state':'sent',
                'partner_id':partner_id.id if partner_id else False,
                'from_number':contacts[0].get("wa_id") if contacts else False,
                'from_name':contacts[0].get("profile").get("name") if contacts else False,
                }
            )
        return
    @http.route('/whatsappApi/hooks', auth='none', csrf=False)
    def index(self, **kw):
        data = json.loads(http.request.httprequest.data)

        _logger.info(data)
        if data:
            for entry in data.get("entry"):
                changes=entry.get("changes")
                for change in changes:
                    if change.get("field")=="messages":
                        value=change.get("value")
                        if value.get("messages") and value.get("contacts"):
                            for message in value.get("messages"):
                                self.process_messages(message,value.get("contacts"))
                        elif value.get("messages") and not value.get("contacts"):
                            for message in value.get("messages"):
                                self.process_messages(message)

        # _logger.info(str(kw))
        # TODO: Hacer verificación de token
        if kw.get('hub.challenge'):
            return kw.get('hub.challenge')
        else:
            return "0"

#     @http.route('/interfaces_whatsapp_api/interfaces_whatsapp_api/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('interfaces_whatsapp_api.listing', {
#             'root': '/interfaces_whatsapp_api/interfaces_whatsapp_api',
#             'objects': http.request.env['interfaces_whatsapp_api.interfaces_whatsapp_api'].search([]),
#         })

#     @http.route('/interfaces_whatsapp_api/interfaces_whatsapp_api/objects/<model("interfaces_whatsapp_api.interfaces_whatsapp_api"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('interfaces_whatsapp_api.object', {
#             'object': obj
#         })
