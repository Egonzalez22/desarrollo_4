from odoo import api, fields, models


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'
    
    # Definimos el tipo de presupuesto
    tipo_presupuesto = fields.Selection([
        ('pharma', 'Pharma'),
        ('medicamentos', 'Médicamentos'),
        ('alta', 'Alta Complejidad'),
        ('analitico', 'Analítico'),
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
        ('calificativo', 'Calificativo'),
    ], string='Tipo de presupuesto', default='pharma')

    # Campos para los informes de pharma
    condicion_pharma = fields.Html(string='Condición Informe Pharma')
    equipos = fields.Html(string='Equipos')
