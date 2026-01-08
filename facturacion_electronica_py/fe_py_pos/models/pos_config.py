from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class PosConfigCustom(models.Model):
    _inherit = 'pos.config'

    diario_electronico = fields.Boolean(string='Diario Electrónico', compute='_compute_diario_electronico')
    tipo_documento_factura = fields.Selection([('factura', 'Factura'), ('autoimpresor', 'Autoimpresor'), ('electronico', 'Electrónico')], string='Tipo documento impresión', default='factura')

    # Campos relacionados a la generación del XML
    iTipTra = fields.Selection(
        string="Tipo de transacción",
        selection=[
            ('1', 'Venta de mercaderia'),
            ('2', 'Prestación de servicios'),
            ('3', 'Mixto'),
            ('4', 'Venta de activo fijo'),
            ('5', 'Venta de divisas'),
            ('6', 'Compra de divisas'),
            ('7', 'Promoción o entrega de muestras'),
            ('8', 'Donación'),
            ('9', 'Anticipo'),
            ('10', 'Compra de productos'),
            ('11', 'Compra de servicios'),
            ('12', 'Venta de crédito fiscal'),
            ('13', 'Muestras médicas'),
        ],
        default='1',
    )
    indicador_presencia = fields.Selection(
        string="Indicador de Presencia",
        selection=[
            ('1', 'Operacion presencial'),
            ('2', 'Operacion electrónica'),
            ('3', 'Operacion telemarketing'),
            ('4', 'Venta a domicilio'),
            ('5', 'Operacion bancaria'),
            ('6', 'Operacion cíclica'),
            ('9', 'Otro'),
        ],
        default='1',
    )

    @api.depends('invoice_journal_id')
    def _compute_diario_electronico(self):
        for record in self:
            record.diario_electronico = record.invoice_journal_id.es_documento_electronico