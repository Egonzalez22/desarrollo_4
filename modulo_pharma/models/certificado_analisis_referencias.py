from odoo import models, fields, api

class CertificadosAnalisisReferencias(models.Model):
    _name = 'certificados.analisis_referencias'
    _description = 'Análisis/Referencias'

    certificado_id = fields.Many2one('certificados.laboratorio', string='Certificado', required=True, ondelete='cascade')
    metodo_id = fields.Many2one('product.template', string='Método', store=True)
    referencia_bibliografica = fields.Char(string='Referencia Bibliográfica', related="metodo_id.referencia_bibliografica")
