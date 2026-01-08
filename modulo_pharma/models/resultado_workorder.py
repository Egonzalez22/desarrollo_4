from odoo import models, fields, api


class ResultadoAlta(models.Model):
    _name = 'resultado.alta'

    certificado_laboratorio_id = fields.Many2one('certificados.laboratorio', string='Certificado de Laboratorio')
    workorder_id = fields.Many2one('mrp.workorder', string='Orden de Trabajo')
    sustancia_activa_id = fields.Many2one('sustancias_activas', string='Sustancias Activas')
    resultado = fields.Float(string="Resultado mg/kg")
    resultado_txt = fields.Char(string="Resultado (comentario)", default="No Detectable")
    lod = fields.Char(string="LOD mg/kg")
    intervalo_referencia = fields.Char(string="Intervalo de Referencia")

    company_id = fields.Many2one('res.company', string="Compañia", related="workorder_id.company_id")

    @api.onchange('resultado')
    def onchangeResultado(self):
        for record in self:
            if record.resultado != 0.0:
                record.resultado_txt = ""


class ResultadoFarma(models.Model):
    _name = 'resultado.farma'

    certificado_laboratorio_id = fields.Many2one('certificados.laboratorio', string='Certificado de Laboratorio')
    workorder_id = fields.Many2one('mrp.workorder', string='Orden de Trabajo')
    resultado = fields.Float(string="Resultado")

    principio_activo_id = fields.Many2one('product.template', string='Principios Activos')
    especificacion = fields.Char(string="Especificación")
    limite_deteccion = fields.Char(string="Límite de detección")

    company_id = fields.Many2one('res.company', string="Compañia", related="workorder_id.company_id")


class ResultadoToxi(models.Model):
    _name = 'resultado.toxi'

    certificado_laboratorio_id = fields.Many2one('certificados.laboratorio', string='Certificado de Laboratorio')
    workorder_id = fields.Many2one('mrp.workorder', string='Orden de Trabajo')
    sustancia_activa_id = fields.Many2one('sustancias_activas', string='Sustancias Activas')
    resultado = fields.Float(string="Resultado")
    resultado_txt = fields.Char(string="Resultado (comentario)", default="No Detectable")
    intervalo_referencia = fields.Char(string="Intervalo de Referencia")
    metodo_id = fields.Many2one('product.product', string="Método", related="workorder_id.product_id")

    company_id = fields.Many2one('res.company', string="Compañia", related="workorder_id.company_id")

    @api.onchange('resultado')
    def onchangeResultado(self):
        for record in self:
            if record.resultado != 0.0:
                record.resultado_txt = ""


class ResultadoAgro(models.Model):
    _name = 'resultado.agro'

    certificado_laboratorio_id = fields.Many2one('certificados.laboratorio', string='Certificado de Laboratorio')
    workorder_id = fields.Many2one('mrp.workorder', string='Orden de Trabajo')
    principio_activo_id = fields.Many2one('product.template', string='Principios Activos')
    resultado = fields.Float(string="Resultado")
    resultado_txt = fields.Char(string="Resultado (comentario)", default="No Detectable")
    tolerancia = fields.Char(string="Tolerancia", default="No Especificado")
    metodo_ensayo_id = fields.Many2one('product.product', string="Método de Ensayo", related="workorder_id.product_id")

    company_id = fields.Many2one('res.company', string="Compañia", related="workorder_id.company_id")

    @api.onchange('resultado')
    def onchangeResultado(self):
        for record in self:
            if record.resultado != 0.0:
                record.resultado_txt = ""