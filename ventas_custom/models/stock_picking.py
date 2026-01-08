from datetime import datetime

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tipo_grupo = fields.Char(string='Nombre grupo', compute='compute_tipo_grupo')

    # Farma
    condicion_almacenamiento = fields.Char(String='Condición de Almacenamiento')
    descipcion_envase = fields.Char(string='Descripción del Envase')
    fabricante = fields.Char(string='Fabricante')
    origen = fields.Char(string='Origen')
    forma_farmaceutica = fields.Char(string='Forma Farmacéutica')
    # Alta complejidad
    procedencia = fields.Char(string='Procedencia/Origen')
    condicion = fields.Char(string='Condición')
    # Agroquimicos
    tipo_solicitud = fields.Char(string='Tipo de Solicitud')
    aspecto = fields.Char(string='Aspecto')
    tipo_envase = fields.Char(string='Tipo Envase')
    concentracion = fields.Char(string='Concentración')
    composicion = fields.Char(string='Composición')
    tipo_formulacion = fields.Char(string='Tipo de Formulación')
    uso = fields.Char(string='Uso')
    importador = fields.Char(string='Importador/Distribuidor/Fabricante')
    fecha_elaboracion = fields.Date(string='Fecha Elaboración')
    lugar_muestreo = fields.Char(string='Lugar de Muestreo')
    color = fields.Char(string='Color')
    densidad = fields.Char(string='Densidad ( g/ml)')
    # Taxicologia
    paciente = fields.Char(string='Paciente')
    sexo = fields.Boolean(string='Sexo (check=M)')
    edad = fields.Char(string='Edad')
    nro_orden = fields.Char(string='Nro. Orden')
    medico = fields.Char(string='Médico')
    codigo_remision = fields.Char(string='Código Remisión')
    almacenamiento = fields.Char(string='Almacenamiento')
    solicitud_urgente = fields.Boolean(string='Tipo Solicitud (check=Urgente)')

    def compute_tipo_grupo(self):
        """"Obtiene el tipo de grupo del presupuesto. Si tipo_grupo = False, no renderiza Datos ANALITICA"""
        for this in self:
            group_type = False
            sale_order = self.env['sale.order'].search([('stock_picking_id', '=', this.id)])
            if sale_order and sale_order.grupo_id:
                group_type = sale_order.grupo_id.tipo_grupo

            this.tipo_grupo = group_type

    def button_imprimir_action(self):
        data = {
            'ids': self.ids,
            'picking_id': self.id,
            'model': 'reporte.muestra',
        }

        return self.env.ref('ventas_custom.reporte_muestra_action').report_action(self, data=data)
