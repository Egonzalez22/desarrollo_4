from odoo import models, fields, api

class CertificadosResultadosObtenidos(models.Model):
    _name = 'certificados.resultados_obtenidos'
    _description = 'Resultados Obtenidos en Certificados'

    certificados_id = fields.Many2one('certificados.laboratorio', string='Certificado', required=True, ondelete='cascade')
    ensayos = fields.Many2one('product.template', string='Ensayos')
    principios_activos = fields.Many2many('product.template', string="Principios Activos")
    resultados = fields.Char(string='Resultados')
    especificacion = fields.Text(string='Especificación')
    limite_deteccion = fields.Text(string='Límite de Detección')
