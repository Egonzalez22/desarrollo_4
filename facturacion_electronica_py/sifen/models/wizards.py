import logging

from odoo import api, exceptions, fields, models

_logger = logging.getLogger(__name__)


class CancelarWizard(models.TransientModel):
    _name = 'fe.cancelar_wizard'
    _description = 'Wizard para cancelar facturas'

    motivo = fields.Char(string='Motivo')

    def action_confirm(self):
        try:
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')

            if active_model == 'account.move':
                record = self.env[active_model].browse(active_id)
                cancelado = record.cancelar_factura(self.motivo)
                # Verificamos si se canceló la factura
                if cancelado:
                    # Sigue el flujo normal de la anulacion
                    record.validar_timbrado()
                    if record.state != 'draft':
                        record.button_draft()
                    record.button_cancel()

                    record.motivo_cancelacion = self.motivo

                    return {'type': 'ir.actions.act_window_close'}
                else:
                    # TODO: Retornar un mensaje indicandole que no se cancelo
                    return {'type': 'ir.actions.act_window_close'}

            return {'type': 'ir.actions.act_window_close'}
        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError(e)

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class InutilizarWizard(models.TransientModel):
    _name = 'fe.inutilizar_wizard'
    _description = 'Wizard para inutilizar facturas'

    motivo = fields.Char(string='Motivo')
    fact_inicio = fields.Char(
        string='Número Inicio del rango del documento',
        default=lambda self: self._context.get('default_fact_inicio'),
    )
    fact_fin = fields.Char(
        string='Número Final del rango del documento',
        default=lambda self: self._context.get('default_fact_fin'),
    )
    # Diario de venta y documento electronico
    journal_id = fields.Many2one('account.journal', string='Diario', domain=[('type', '=', 'sale'), ('es_documento_electronico', '=', True)])
    nro_timbrado = fields.Char(string='Número de timbrado')
    establecimiento = fields.Char(string='Establecimiento')
    punto_expedicion = fields.Char(string='Punto de expedición')
    tipo_documento_electronico = fields.Selection(
        string="Tipo de documento",
        selection=[
            ('out_invoice', 'Factura'),
            ('out_refund', 'Nota de credito'),
            ('nota_remision', 'Nota de remision'),
            ('autofactura', 'Autofactura'),
            ('nota_debito', 'Nota de débito'),
        ],
        default="out_invoice",
        required=True,
    )

    def action_confirm(self):
        try:
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')

            if active_model == 'account.move':
                record = self.env[active_model].browse(active_id)
                inutilizado = record.inutilizar_factura(self.fact_inicio, self.fact_fin, self.motivo)
                # Verificamos si se canceló la factura
                if inutilizado:
                    return {'type': 'ir.actions.act_window_close'}
                else:
                    # TODO: Retornar un mensaje indicandole que no se inutilizo
                    return {'type': 'ir.actions.act_window_close'}

            return {'type': 'ir.actions.act_window_close'}
        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError(e)

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def action_confirm_rango(self):
        try:
            self.validar_campos_inutilizar_rango()

            # Creamos un logger del invoice
            fe_rango_object = (
                self.env['fe.inutilizar_rango']
                .sudo()
                .create(
                    {
                        'fact_inicio': self.fact_inicio,
                        'fact_fin': self.fact_fin,
                        'motivo': self.motivo,
                        'journal_id': self.journal_id.id,
                        'nro_timbrado': self.nro_timbrado,
                        'establecimiento': self.establecimiento,
                        'punto_expedicion': self.punto_expedicion,
                        'tipo_documento_electronico': self.tipo_documento_electronico,
                    }
                )
            )
            self.env.cr.commit()

            data = {
                'fact_inicio': self.fact_inicio,
                'fact_fin': self.fact_fin,
                'motivo': self.motivo,
                'journal_id': self.journal_id.id,
                'nro_timbrado': self.nro_timbrado,
                'establecimiento': self.establecimiento,
                'punto_expedicion': self.punto_expedicion,
                'tipo_documento_electronico': self.tipo_documento_electronico,
            }
            # Pasamos dos veces el objeto, porque en el mismo objeto se guarda el logger
            inutilizado = self.env["fe.de"].inutilizar_rango_facturas(data, fe_rango_object, fe_rango_object)
            return {'type': 'ir.actions.act_window_close'}

        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError(e)

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        # Obtenemos el timbrado activo
        if self.journal_id:
            timbrado = self.journal_id.timbrados_ids.filtered(
                lambda x: x.active is True and x.tipo_documento == self.tipo_documento_electronico
            )
            if timbrado:
                self.nro_timbrado = timbrado.name
                self.establecimiento = timbrado.nro_establecimiento
                self.punto_expedicion = timbrado.nro_punto_expedicion

    def validar_campos_inutilizar_rango(self):
        # 1 - Validamos que el nro de factura desde sea menor al nro de factura hasta
        if int(self.fact_inicio) > int(self.fact_fin):
            raise exceptions.ValidationError('El número de factura inicio debe ser menor al número de factura fin')
