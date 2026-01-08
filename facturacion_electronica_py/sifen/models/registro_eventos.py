import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FELote(models.Model):
    _name = 'fe.lote'
    _description = 'Registro de lotes de facturas enviadas a SIFEN'

    name = fields.Char(string="Nombre")
    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    estado_set = fields.Selection(
        string="Estado",
        selection=[
            ('pendiente', 'Pendiente'),  # Se asociaron las facturas
            ('en_proceso', 'En procesamiento'),  # Se recibio el lote correctamente
            ('reenviar', 'Reenviar'),  # Se reenvia por error al recibir lote
            ('error', 'Error SIFEN'),  # Error en respuesta de SIFEN status != 200
            ('aprobado', 'Aprobado'),  # Finalizado correctamente
            ('rechazado', 'Rechazado'),  # Finalizado con error
            ('expirado', 'Tiempo expirado'),  # Tiempo de consulta expirado
        ],
        copy=False,
        default="pendiente",
    )
    estado_lote = fields.Selection(
        string="Estado Lote",
        selection=[
            ('creado', '1 - Creado'),  # Al momento de asociar los DE al lote
            ('en_proceso', '2 - En procesamiento'),  # Se recibio el lote correctamente
            ('finalizado', '3 - Finalizado'),  # Procesado, sea con error o aprobado
        ],
        copy=False,
        default="creado",
    )
    tipo_documento_electronico = fields.Selection(
        string="Tipo de documento",
        selection=[
            ('out_invoice', 'Factura'),
            ('out_refund', 'Nota de crédito'),
            ('nota_remision', 'Nota de remisión'),
            ('autofactura', 'Autofactura'),
            ('nota_debito', 'Nota de débito'),
        ],
        default="out_invoice",
    )
    fecha_procesamiento = fields.Datetime(string="Fecha de procesamiento")
    codigo_resultado = fields.Char('Código del resultado del lote')
    mensaje_resultado = fields.Char('Mensaje del resultado del lote')
    numero_lote = fields.Char('Número de lote')
    tiempo_procesamiento = fields.Char('Tiempo de procesamiento')

    zipfile_name = fields.Char(string="Nombre ZIP", copy=False)
    zipfile = fields.Binary(string="ZIP", copy=False)

    invoice_ids = fields.One2many('account.move', 'lote_id', string='Facturas', copy=False)
    remision_ids = fields.One2many('notas_remision_account.nota.remision', 'lote_nr_id', string='Remisiones', copy=False)
    lote_loggers_ids = fields.One2many('fe.lote_loggers', 'lote', string='Loggers', copy=False)

    # Si el envio del lote falla, se guarda el intento de envio para reintentar un maximo de X veces
    intento_envio = fields.Integer(string="Intento de envío", default=0, copy=False)

    @api.model
    def create(self, vals):
        res = super(FELote, self).create(vals)
        if res:
            res.write({'name': res.id})

        return res


class FELoteLoggers(models.Model):
    _name = 'fe.lote_loggers'
    _description = 'Se guarda el log de request por cada lote enviado a SIFEN'

    name = fields.Char(string="Nombre")
    request = fields.Text(string='Request', copy=False)
    response = fields.Text(string='Response', copy=False)
    status_code = fields.Char(string='Status Code', copy=False)
    accion = fields.Char(string='Acción', copy=False)

    lote = fields.Many2one('fe.lote', string='Lote', copy=False)

    @api.model
    def create(self, vals):
        res = super(FELoteLoggers, self).create(vals)
        if res:
            res.write({'name': res.id})

        return res


class FEDELoggers(models.Model):
    _name = 'fe.de_loggers'
    _description = 'Se guarda el log de request por cada factura enviada a SIFEN'

    name = fields.Char(string="Nombre")
    request = fields.Text(string='Request', copy=False)
    response = fields.Text(string='Response', copy=False)
    status_code = fields.Char(string='Status Code', copy=False)
    accion = fields.Char(string='Acción', copy=False)

    invoice = fields.Many2one('account.move', string='Factura', copy=False)
    remision_id = fields.Many2one('notas_remision_account.nota.remision', string='Remision', copy=False)
    tipo_documento_electronico = fields.Selection(
        string="Tipo de documento",
        selection=[
            ('out_invoice', 'Factura'),
            ('out_refund', 'Nota de crédito'),
            ('nota_remision', 'Nota de remisión'),
            ('autofactura', 'Autofactura'),
            ('nota_debito', 'Nota de débito'),
        ],
        default="out_invoice",
    )

    # Archivos
    xml_firmado_name = fields.Char(string="Nombre XML Firmado", copy=False)
    xml_firmado = fields.Binary(string="XML Firmado", copy=False)
    xml_soap_name = fields.Char(string="Nombre XML Soap", copy=False)
    xml_soap = fields.Binary(string="XML Soap", copy=False)
    json_file_name = fields.Char(string="Nombre JSON", copy=False)
    json_file = fields.Binary(string="JSON", copy=False)

    @api.model
    def create(self, vals):
        res = super(FEDELoggers, self).create(vals)
        if res:
            res.write({'name': res.id})

        return res


class FEInutilizarRango(models.Model):
    _name = 'fe.inutilizar_rango'
    _description = 'Registro de los rangos de facturas inutilizadas'

    name = fields.Char(string="Nombre")
    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    request = fields.Text(string='Request')
    response = fields.Text(string='Response')
    status_code = fields.Char(string='Status Code')
    status = fields.Selection(
        string="Estado",
        selection=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')],
        copy=False,
        default="pendiente",
    )

    fecha_procesamiento = fields.Datetime(string="Fecha de procesamiento")
    codigo_resultado = fields.Char('Código del resultado')
    mensaje_resultado = fields.Char('Mensaje del resultado')
    mensaje_resultado_detalle = fields.Char('Mensaje del resultado')
    id_resultado = fields.Char('ID de resultado')

    motivo = fields.Char(string='Motivo')
    fact_inicio = fields.Integer(string='Número Inicio del rango del documento')
    fact_fin = fields.Integer(string='Número Final del rango del documento')
    journal_id = fields.Many2one('account.journal', string='Diario')
    nro_timbrado = fields.Char(string='Número de timbrado')
    establecimiento = fields.Char(string='Establecimiento')
    punto_expedicion = fields.Char(string='Punto de expedición')
    # TODO: Esta serie no se utiliza aun en ningun lugar, hay que agregar
    serie_numeracion = fields.Char(string='Serie')
    tipo_documento_electronico = fields.Selection(
        string="Tipo de documento",
        selection=[
            ('out_invoice', 'Factura'),
            ('out_refund', 'Nota de crédito'),
            ('nota_remision', 'Nota de remisión'),
            ('autofactura', 'Autofactura'),
            ('nota_debito', 'Nota de débito'),
        ],
        default="out_invoice",
    )

    @api.model
    def create(self, vals):
        res = super(FEInutilizarRango, self).create(vals)
        if res:
            res.write({'name': res.id})

        return res
