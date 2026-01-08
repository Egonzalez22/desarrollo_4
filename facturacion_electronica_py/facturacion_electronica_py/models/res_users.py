from odoo import fields, api, models, exceptions


class ResUsers(models.Model):
    _inherit = 'res.users'

    cargo = fields.Char(string="Cargo")
    tipo_documento = fields.Selection(
        string="Tipo de Documento",
        selection=[
            ('1', 'Cédula paraguaya'),
            ('2', 'Pasaporte'),
            ('3', 'Cédula extranjera'),
            ('4', 'Carnet de residencia'),
            ('9', 'Otro'),
        ],
        default="1",
        track_visibility="onchange",
    )

    nro_documento = fields.Char(string="Número de Documento", copy=False)
