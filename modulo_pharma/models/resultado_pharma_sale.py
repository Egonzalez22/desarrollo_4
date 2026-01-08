from odoo import models, fields, api


class ResultadosPharmaSale(models.Model):
    _name = 'resultados.pharma.sale'
    resultado_pharma_id = fields.Many2one('resultados.pharma', string='Resultado Pharma')
    ensayo_muestra_line = fields.Many2one('product.template', string="Ensayo")
    principio_activo =  fields.Many2one('product.template', string='Principio Activo')
    resultado = fields.Char(string="Resultado") 
    limite_aceptacion = fields.Char(string="Limite de Aceptacion") 
    limite_deteccion = fields.Char(string="Limite de Deteccion") 
    # vencimiento = fields.Date(string="Vencimiento")
    # conservacion =  fields.Char(string="Conservación")
    # humedad = fields.Float(string="Humedad")
    # lote = fields.Char(string="Lote")


