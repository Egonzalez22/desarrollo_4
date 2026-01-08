from odoo import models, fields, api

class CertificadoPropiedadesFisicas(models.Model):
    _name = 'certificados.propiedades_fisicas'
    _description = 'Propiedades Físicas'

    certificado_id = fields.Many2one('certificados.laboratorio', string='Certificado', required=True, ondelete='cascade')
    aspecto = fields.Char(string="Aspecto")
    color = fields.Char(string="Color")
    densidad = fields.Char(string="Densidad")