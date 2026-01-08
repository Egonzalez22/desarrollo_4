from odoo import _, api, fields, models


class WhatsappMessageTemplate(models.Model):
    _name = 'interfaces_whatsapp_api.message.template'
    _description = 'Plantilla de mensaje'


    name=fields.Char(string="Nombre de la plantilla")
