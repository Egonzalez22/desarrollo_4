from odoo import models, fields, api

class CertificadoEstandarAgro(models.Model):
    _name = 'certificados.estandar_agro'
    _description = 'Estandar'

    certificado_id = fields.Many2one('certificados.laboratorio', string='Certificado', required=True, ondelete='cascade')
    principio_activo_id = fields.Many2one('product.template', string="Principios Activos")
    lote = fields.Char(string="Lote")
    conservacion = fields.Char(string="Conservación")
    vencimiento = fields.Date(string="Vencimiento")
    titulo = fields.Float(string="% Título")
    humedad = fields.Float(string="% Húmedad")
