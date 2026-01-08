from odoo import _, api, fields, models,exceptions




class AccountMove(models.Model):
    _inherit = 'account.move'


    # Campos relacionados a factura de exportación
    export_tipo_operacion = fields.Selection([('Exportación', 'Exportación')], default='Exportación', string="Tipo de operación")
    export_condicion_negociacion = fields.Selection([('cif', 'CIF'), ('fob', 'FOB'), ('otros', 'Otros')], string="Condición de negociación")
    export_pais_destino = fields.Many2one('res.country', string="País de destino")
    export_exportador_nacional = fields.Many2one('res.partner', string="Empresa Fletera o Exportador nacional")
    export_agente_transporte = fields.Many2one('res.partner', string="Agente de transporte")
    export_instruccion_pago = fields.Char(string="Instrucción de pago")
    export_numero_embarque = fields.Char(string="Número de embarque")
    export_numero_manifiesto = fields.Char(string="Número de manifiesto")
    export_numero_barcaza = fields.Char(string="Número de barcaza")
    export_informacion_adicional = fields.Text(string="Información adicional")

    es_factura_exportacion = fields.Boolean("Es factura de exportación", compute="_compute_es_factura_exportacion")

    @api.depends('journal_id')
    def _compute_es_factura_exportacion(self):
        for record in self:
            # La factura debe ser del tipo out_invoice (cliente) y el diario debe tener el check de factura de exportación
            if record.move_type == 'out_invoice':
                record.es_factura_exportacion = record.journal_id.es_factura_exportacion
            else:
                record.es_factura_exportacion = False