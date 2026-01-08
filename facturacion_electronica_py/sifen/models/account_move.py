import json
import math
import re

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import (AccessError, RedirectWarning, UserError,
                             ValidationError)


def round_up(n, decimals=0):
    multiplier = 10**decimals
    return math.ceil(n * multiplier) / multiplier


class AccountMove(models.Model):
    _inherit = 'account.move'

    naturaleza_vendedor = fields.Selection(string="Naturaleza del vendedor", selection=[('1', 'No contribuyente'), ('2', 'Extranjero')])
    fecha_remision = fields.Date(string="Fecha de remisión", copy=False)
    invoice_datetime = fields.Datetime(string="Fecha y Hora de Emisión", copy=False)
    nro_factura_asociada = fields.Many2one(
        'account.move',
        string="Factura asociada",
        copy=False,
        domain="[('move_type', '=', 'out_invoice'), ('partner_id', '=', partner_id)]",
    )
    # TODO: Se debe dejar de referenciar a este campo, para permitir multiples anticipo.
    # Se deja temporalmente para migrar los datos luego
    factura_anticipo_id = fields.Many2one(
        'account.move', 
        string="Factura de anticipo", 
        copy=False
    )
    facturas_anticipo_asociadas = fields.Many2many(
        'account.move', 
        relation='account_move_anticipo_rel',
        column1='move_id',
        column2='anticipo_id',
        string="Facturas de anticipo",
        copy=False,
        domain="[('partner_id', '=', partner_id)]",
    )
    nota_remision_asociadas = fields.Many2many(
        'notas_remision_account.nota.remision',
        string="Notas de remisión",
        copy=False,
        domain="[('partner_id', '=', partner_id)]",
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
    )
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
    )
    iTImp = fields.Selection(
        string="Tipo de impuesto afectado",
        selection=[('1', 'IVA'), ('2', 'ISC'), ('3', 'Renta'), ('4', 'Ninguno'), ('5', 'IVA - Renta')],
    )

    show_reset_to_draft_button = fields.Boolean(compute='_compute_show_reset_to_draft_button')

    def unlink(self):
        # facturacion_electronica/models/account_move.py
        """
        Si la factura ya tiene una númeración creada, no se puede eliminar la factura independientemente del estado
        """

        for move in self:
            # Si viene la bandera force_delete_fe, no se ingresa a la validación
            if not self._context.get('force_delete_fe', False):
                patron = re.compile(r'((^\d{3})[-](\d{3})[-](\d{7}$)){1}')
                if move.es_documento_electronico() and move.name and patron.match(move.name):
                    msg = "No se puede eliminar una factura que ya tiene un número asignado. \nSi está aprobado por SIFEN, puede cancelar. \nSi no está aprobado por SIFEN, puede inutilizar."
                    raise ValidationError(_(msg))

        return super(AccountMove, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        # facturacion_electronica/models/account_move.py
        moves = super(AccountMove, self).create(vals_list)

        self.create_fe_vals(moves, vals_list)

        return moves

    def create_fe_vals(self, moves, vals_list):
        """
        Al momento de crear una factura, agregamos validaciones relacionadas a FE.
        Se separa en un metodo aparte para poder sobreescribirlo facilmente de ser necesario
        """
        for move, vals in zip(moves, vals_list):  

            # Verificamos si la factura es anticipo
            is_downpayment = move._is_downpayment()
            if is_downpayment:
                move.iTipTra = '9'

            # Si no es anticipo, pero tiene lineas de anticipo. Agregamos la factura de anticipo
            if not is_downpayment:
                downpayment_moves = move.line_ids._get_downpayment_lines().mapped("move_id")
                move.facturas_anticipo_asociadas = downpayment_moves


    @api.depends('company_id', 'invoice_filter_type_domain', 'tipo_documento')
    def _compute_suitable_journal_ids(self):
        if self.env.company.country_id.name=='Paraguay':
            # Es el mismo metodo en 15 y 16
            for m in self:
                journal_type = m.invoice_filter_type_domain or 'general'
                company_id = m.company_id.id or self.env.company.id
                domain = [('company_id', '=', company_id), ('type', '=', journal_type)]

                # Solamente si es diario de ventas se filtra por tipo de documento
                if journal_type == 'sale' and m.tipo_documento != "autofactura":
                    # TODO: Se debe validar que el diario sea FE?
                    domain += [('timbrados_ids.tipo_documento', '=', m.tipo_documento)]

                print(domain)

                m.suitable_journal_ids = self.env['account.journal'].search(domain)
                print(m.suitable_journal_ids)
        else:
            return super(AccountMove,self)._compute_suitable_journal_ids()
        
    @api.depends('move_type', 'tipo_documento')
    def _compute_invoice_filter_type_domain(self):
        if self.env.company.country_id.name=='Paraguay':
            # Es el mismo metodo en 15 y 16
            for move in self:
                if move.is_sale_document(include_receipts=True) and move.tipo_documento != "nota_debito":
                    move.invoice_filter_type_domain = 'sale'
                elif move.is_purchase_document(include_receipts=True) and move.tipo_documento != "autofactura":
                    move.invoice_filter_type_domain = 'purchase'
                elif move.tipo_documento == "nota_debito":
                    move.invoice_filter_type_domain = 'sale'
                elif move.tipo_documento == "autofactura":
                    move.invoice_filter_type_domain = 'purchase'
                else:
                    move.invoice_filter_type_domain = False
        else:
            return super(AccountMove,self)._compute_invoice_filter_type_domain()

    @api.depends('restrict_mode_hash_table', 'state')
    def _compute_show_reset_to_draft_button(self):
        for move in self:
            # Solamente se puede restablecer a borrador, facturas que tengan un estado definido
            move.show_reset_to_draft_button = (
                not move.restrict_mode_hash_table
                and move.state in ('posted', 'cancel')
                and move.estado_set in ("borrador", "error_sifen", "lote_rechazado", "rechazado")
            )

    def _post(self, soft=True):
        res = super(AccountMove, self)._post()
        for rec in self:
            # Si es documento electronico, agregamos las validaciones para facturas de venta, notas de credito y notas de debito
            if rec.es_documento_electronico() and rec.move_type in ['out_invoice', 'out_refund', 'in_invoice']:
                rec.preparar_documento_electronico()

                # Si tiene remisiones asociadas, guardamos el ID de la factura en cada remision
                if rec.nota_remision_asociadas:
                    for remision in rec.nota_remision_asociadas:
                        remision.write({'invoice_id': rec.id})

        return res

    def action_reverse(self):
        action = super(AccountMove, self).action_reverse()

        # # TODO: Ver si es necesario esto y como solucionar. Filtra los diarios pero sigue tirando un diario por defecto que no esta en el filtro
        # if self.es_documento_electronico() and self.move_type in ['out_invoice']:
        #     # Obtenemos los diarios que son de FE y NC
        #     diarios = self.env['account.journal'].search([('timbrados_ids.tipo_documento', '=', 'out_refund')])
        #     context = json.loads(action['context'])
        #     context['default_available_journal_ids'] = diarios.ids
        #     action['context'] = str(context)

        return action

    def button_anular(self):
        # Se sobreescribe de account_move interfaces_timbrado
        for i in self:
            # Si es documento electronico y esta aprobado, enviamos a la SET
            if i.es_documento_electronico():
                if i.estado_set == "aprobado":
                    return i.button_cancelar_factura()
            else:
                i.validar_timbrado()
                if i.state != 'draft':
                    i.button_draft()
                i.button_cancel()
                return

    def button_cancelar_factura(self):
        view_id = self.env.ref('sifen.cancelar_factura_wizard_form')
        return {
            'name': 'Cancelar Factura',
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'fe.cancelar_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def button_inutilizar_factura(self):
        # Solo se pueden inutilizar facturas rechazadas
        if self.estado_set not in ["rechazado"]:
            raise exceptions.ValidationError(_("Solo se pueden inutilizar facturas rechazadas o en borrador"))
        
        # Verificamos que la factura tenga CDC
        if not self.cdc:
            raise exceptions.ValidationError(_("La factura debe tener un CDC para poder inutilizarla"))

        view_id = self.env.ref('sifen.inutilizar_factura_wizard_form')
        nro_factura = self.name.split("-")[2]

        return {
            'name': 'Inutilizar Factura',
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'fe.inutilizar_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_fact_inicio': nro_factura,
                'default_fact_fin': nro_factura,
            },
        }

    @api.model
    def format_monto_kude(self, monto):
        currency_id = self.currency_id
        lang_str = self._context.get('lang')
        lang_id = self.env['res.lang'].search([('iso_code', '=', 'es_PY')])

        fmt = "%.{0}f".format(currency_id.decimal_places or 0)
        resultado = lang_id.format(fmt, monto, grouping=True)
        return resultado

    def amount_to_text_fe(self, amount, currency=False):
        # FIX Temporal para obtener el mismo resultado que se muestra en el valor numerico del kude
        # Una vez que se implemente la precision decimal de la moneda en todos los campos del tipo moneda, ya no será necesario
        converted_amount = float(self.format_monto_kude(amount).replace('.', '').replace(',', '.'))

        convert_amount_in_words = self.env['interfaces_tools.tools'].numero_a_letra(converted_amount)
        return convert_amount_in_words

 # def _search_default_journal(self):
    #     if self.payment_id and self.payment_id.journal_id:
    #         return self.payment_id.journal_id
    #     if self.statement_line_id and self.statement_line_id.journal_id:
    #         return self.statement_line_id.journal_id
    #     if self.statement_line_ids.statement_id.journal_id:
    #         return self.statement_line_ids.statement_id.journal_id[:1]

    #     if self.is_sale_document(include_receipts=True):
    #         journal_types = ['sale']
    #     elif self.is_purchase_document(include_receipts=True):
    #         journal_types = ['purchase']
    #     elif self.payment_id or self.env.context.get('is_payment'):
    #         journal_types = ['bank', 'cash']
    #     else:
    #         journal_types = ['general']

    #     company_id = (self.company_id or self.env.company).id
    #     # domain = [('company_id', '=', company_id), ('type', 'in', journal_types), ('tipo_documento_electronico','=', self.tipo_documento)]
    #     journal_ids = []
    #     journal_ids = self.env['account.journal'].search([('company_id', '=', company_id), ('type', 'in', journal_types)])
    #     if (
    #         journal_ids
    #         and 'bank' not in journal_types
    #         and 'cash' not in journal_types
    #         and 'general' not in journal_types
    #         and ("purchase" in journal_types and self.tipo_documento != "autofactura")
    #     ):
    #         journal_ids = journal_ids.filtered(lambda x: self.tipo_documento in x.timbrados_ids.mapped('tipo_documento'))

    #     domain = [('id', 'in', journal_ids.ids)]

    #     journal = None
    #     currency_id = self.currency_id.id or self._context.get('default_currency_id')
    #     if currency_id and currency_id != self.company_id.currency_id.id:
    #         currency_domain = domain + [('currency_id', '=', currency_id)]
    #         journal = self.env['account.journal'].search(currency_domain, limit=1)

    #     if not journal:
    #         journal = self.env['account.journal'].search(domain, limit=1)

    #     if not journal:
    #         company = self.env['res.company'].browse(company_id)

    #         error_msg = _(
    #             "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
    #             company_name=company.display_name,
    #             journal_types=', '.join(journal_types),
    #         )
    #         raise UserError(error_msg)

    #     return journal

    # TODO: Verificar si se debe limpiar el nro de factura y las lineas
    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     """
    #     Al cambiar el partner, se debe limpiar el nro_factura_asociada
    #     """
    #     for record in self:
    #         # Si el tipo de movimiento es nota de credito
    #         if record.move_type == 'out_refund':
    #             record.nro_factura_asociada = False
    #             record.update({'invoice_line_ids': [(5, 0, 0)]})

    # @api.onchange('nro_factura_asociada')
    # def _onchange_nro_factura_asociada(self):
    #     """
    #     Al cambiar la factura asociada, se debe copiar las lineas a la nueva factura
    #     """
    #     for record in self:
    #         if record.nro_factura_asociada:
    #             # Limpiamos las lineas
    #             record.update({'invoice_line_ids': [(5, 0, 0)]})

    #             # Recorremos las lineas de la factura asociada
    #             for line in record.nro_factura_asociada.invoice_line_ids:
    #                 # Creamos la linea
    #                 new_line = {
    #                     'product_id': line.product_id.id,
    #                     'name': line.name,
    #                     'account_id': line.account_id.id,
    #                     'quantity': line.quantity,
    #                     'product_uom_id': line.product_uom_id.id,
    #                     'currency_id': line.currency_id.id,
    #                     'tax_ids': [(6, 0, line.tax_ids.ids)],
    #                     'price_unit': line.price_unit,
    #                     'discount': line.discount,
    #                     'price_subtotal': line.price_subtotal,
    #                     'price_total': line.price_total,
    #                 }
    #                 record.update({'invoice_line_ids': [(0, 0, new_line)]})

    #             record._onchange_invoice_line_ids()
    #             record._move_autocomplete_invoice_lines_values()