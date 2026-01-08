from odoo import models, fields, api


class ResultadosPharmaDetalle(models.Model):
    _name = 'resultados.pharma.detalle'

    resultado_pharma_id = fields.Many2one('resultados.pharma', string='Resultado Pharma')
    certificado_laboratorio_id = fields.Many2one('certificados.laboratorio', string='Certificado de Laboratorio')
    principios_activos = fields.Many2one('product.template', string='Principio Activo')
    lote = fields.Char(string="Lote")
    vencimiento = fields.Date(string="Vencimiento") 
    titulo = fields.Float(string="% Titulo")
    conservacion =  fields.Char(string="Conservación")
    humedad = fields.Float(string="% Humedad")

