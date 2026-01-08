from odoo import models, fields, api, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    proveedor_facturador_electronico = fields.Boolean('El proveedor es Facturador Electrónico', default=False)
    res90_tipo_identificacion = fields.Selection([
        ('11', 'RUC'), 
        ('12', 'Cédula de identidad'), 
        ('13', 'Pasaporte'), 
        ('14', 'Cédula extranjero'), 
        ('15', 'Sin nombre'), 
        ('16', 'Diplomático'), 
        ('17', 'Identificación tributaria')
    ])
