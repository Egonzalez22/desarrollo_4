from odoo import fields, api, models, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contribuyente = fields.Boolean(string="Contribuyente", default=True, required=False)

    # Tipo de Documento 1= Cédula paraguaya 2= Pasaporte 3= Cédula extranjera 4= Carnet de residencia 5= Innominado
    # 6=Tarjeta Diplomática de exoneración fiscal 9= Otro
    tipo_documento = fields.Selection(
        string="Tipo de Documento",
        selection=[
            ('1', 'Cédula paraguaya'),
            ('2', 'Pasaporte'),
            ('3', 'Cédula extranjera'),
            ('4', 'Carnet de residencia'),
            ('5', 'Innominado'),
            ('6', 'Tarjeta Diplomática de exoneración fiscal'),
            ('9', 'Otro'),
        ],
        default="1",
        track_visibility="onchange",
    )

    nro_documento = fields.Char(string="Número de Documento", copy=False)

    nombre_fantasia = fields.Char(string="Nombre de fantasia")

    @api.onchange('nro_documento')
    def _onchange_nro_documento(self):
        # Cuando cambia el texto de nro_documento, se actualiza el campo vat
        if self.nro_documento:
            self.obviar_validacion = True
            self.vat = self.nro_documento

    @api.model
    def poblar_vat_desde_ci(self):
        # 1 - Obtenemos todos los contactos que tienen nro_documento, sin vat y no son contribuyentes
        domain = [
            ('nro_documento', '!=', False),
            ('vat', 'in', ['', False]),
            ('contribuyente', '=', False),
        ]
        partners = self.env['res.partner'].search(domain)

        # 2 - Iteramos sobre los contactos y actualizamos el campo vat con el valor de nro_documento
        for partner in partners:
            partner.obviar_validacion = True
            partner.with_context(no_vat_validation=True).vat = partner.nro_documento
            
        self.env.cr.commit()
