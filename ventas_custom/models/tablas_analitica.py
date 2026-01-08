# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class Grupo(models.Model):
    _name = 'ventas.grupo'

    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripción')
    usa_sustancias = fields.Boolean(string='Usa Sustancias Activas')
    es_acreditado = fields.Boolean(string='Es Acreditado')
    observacion = fields.Html(string='Observación')
    tipo_grupo = fields.Selection([
        ('toxicologico', 'Toxicológico'),
        ('farma', 'Farma'),
        ('alta_complejidad', 'Alta Complejidad'),
        ('agroquimico', 'Agroquímico'),
    ], string='Tipo de Presupuesto', required=True, default='toxicologico')
    tipo_documento = fields.Selection([
        ('Presupuesto', 'Presupuesto'),
        ('Solicitud de Análisis de Muestras', 'Solicitud de Análisis de Muestras'),
        ('Certificado', 'Certificado'),
        ('Informe de control', 'Informe de control'),
    ], string='Tipo de Documento')
    nombre_iso = fields.Char(string='Nombre ISO del Documento')
    fecha_desde = fields.Date(string='Fecha de inicio de vigencia')
    fecha_hasta = fields.Date(string='Fecha fin de vigencia')
    notas = fields.Html(string='Notas')
    abreviaturas = fields.Html(string='Abreviaturas')
    equipos = fields.Html(string='Equipos')
    plazo_entrega = fields.Html(string='Plazo de Entrega')
    mantenimiento_oferta = fields.Html(string='Mantenimiento de oferta')
    entrega_resultado = fields.Html(string='Entrega de resultado')

    regente = fields.Char(string="Regente")
    gerencia_tecnica = fields.Char(string="Gerencia Técnica")


class Matriz(models.Model):
    _name = 'ventas.matriz'

    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripción')
    grupo_id = fields.Many2one('ventas.grupo', string='Grupos')


class Metodologia(models.Model):
    _name = 'ventas.metodologia'

    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripción')
    matriz_ids = fields.Many2many('ventas.matriz', string='Matrices')


class Motivo(models.Model):
    _name = 'ventas.motivo'

    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripción')


class Presentacion(models.Model):
    _name = 'ventas.presentacion'

    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    name = fields.Char(string='Nombre', required=True)
    codigo_corto = fields.Char(string='Código Corto')


class Volumen(models.Model):
    _name = 'ventas.volumen'

    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripción')

class MetodologiaAnalisis(models.Model):
    _name = 'ventas.metodologia_analisis'

    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    name = fields.Char(string='Nombre', required=True)